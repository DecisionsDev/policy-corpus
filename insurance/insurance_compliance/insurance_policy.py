import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from common.abstract_policy import Policy

from datetime import date, timedelta
from typing import Tuple
from insurance.insurance_compliance.insurance_request import CarInsuranceRequest, Vehicle, Applicant, \
    DrivingLicense


class CarInsurancePolicy(Policy):

    LOCAL_COUNTRIES_ABBREVIATIONS = ["us", "usa", "united states", "united states of america"]
    STATES = ["california", "texas", "florida", "ohio"]

    MINIMUM_CREDIT_SCORE = 500
    CREDIT_SCORE_FEE_THRESHOLD = 650

    def check_address_validity(self, address: dict) -> bool:
        # OTHER checks

        return (address and str.lower(address.setdefault("country", "")) in self.LOCAL_COUNTRIES_ABBREVIATIONS
                and str.lower(address.setdefault("state", "")) in self.STATES)

    def test_eligibility(self, case) -> Tuple:
        if not isinstance(case, CarInsuranceRequest):
            case = CarInsuranceRequest.from_dict(case)

        primary_applicant = case.primary_applicant()
        if not primary_applicant:
            return False, None, "No primary applicant found."

        today_date = date.today()
        # Check applicant age
        age = (today_date - primary_applicant.birth_date).days // 365
        if age < 18:
            return False, None, "Primary policyholder must be at least 18 years old."
        if age >= 75:
            return False, None, "Applicants over 75 may require additional medical assessments."

        # Check driver’s license validity
        for applicant in case.applicants:
            if applicant.driving_license.status != "valid":
                return False, None, "All applicants must have a valid driver’s license."
            if applicant.driving_license.issue_date > today_date:
                return False, None, "All applicants must have an up-to-date driver’s license."
            if (str.lower(applicant.driving_license.issue_country) not in self.LOCAL_COUNTRIES_ABBREVIATIONS
                    and not applicant.driving_history):
                return (False, None,
                        "International drivers must provide additional documentation or proof of driving history.")

        # Check vehicle ownership within family members
        vehicle_owner_valid = any(
            case.vehicle.registered_on == applicant or
            case.vehicle.registered_on in applicant.family_members
            for applicant in case.applicants
        )
        if not vehicle_owner_valid:
            return (False, None,
                    "The vehicle must be registered in the name of the applicant or an immediate family member.")

        # Check vehicle use
        if case.vehicle.vehicle_use != "personal":
            return False, None, "The vehicle must be used primarily for personal use."

        # Check vehicle safety inspections
        if not case.vehicle.passed_safety_inspections:
            return False, None, "The vehicle must pass required safety inspections."

        # Check the vehicles age
        if (today_date - case.vehicle.date_creation).days // 365 > 20:
            return False, None, "The vehicle older than 20 years cannot be covered"

        # Check driving record
        violation_threshold = 3
        violation_timeframe = today_date - timedelta(days=5 * 365)

        overall_minor_violations = 0

        for applicant in case.applicants:
            minor_violations = 0

            for violation in applicant.driving_history:
                violation_date = violation.get("date")
                if violation_date and date.fromisoformat(violation_date) >= violation_timeframe:
                    if violation.get("type") in ["DUI", "reckless driving"]:
                        return False, None, "Major violations impact eligibility."
                    else:
                        minor_violations += 1
            if minor_violations >= violation_threshold:
                return False, None, "Too many minor violations in the last five years."

            # Check recent license suspensions or revocations
            for status_record in applicant.driving_license.status_history:
                if status_record.get("status") in ["suspended", "revoked"]:
                    status_date = status_record.get("date")
                    if status_date and date.fromisoformat(status_date) >= violation_timeframe:
                        return (False, None,
                                "Recent license suspensions or revocations result in disqualification.")
            overall_minor_violations += minor_violations

        # Check insurance history
        for applicant in case.applicants:
            # TODO there might be better ways to detect lapses
            if any(record.get("lapse") for record in applicant.history_insurance_coverage):
                return False, None, "Lapses in prior insurance coverage may impact eligibility."
            if any(record.get("fraud") for record in applicant.history_insurance_coverage):
                return False, None, "A history of insurance fraud may impact eligibility."
            if sum(1 for record in applicant.history_insurance_coverage if record.get("claims")) > 3:
                return False, None, "Frequent insurance claims may impact eligibility."
            if any(record.get("cancellation_reason") == "non-payment" for record in applicant.history_insurance_coverage):
                return False, None, "Policy cancellations due to non-payment may impact eligibility."

        # Check residency
        for applicant in case.applicants:
            if not self.check_address_validity(applicant.address):
                return False, None, "All applicants must reside in the country and state where the policy is issued."

        # Check minimum liability coverage
        if case.liability_coverage < case.state_min_liability:
            return False, None, "Coverage must meet the state's minimum liability requirements."

        # Credit Score (if applicable)
        for applicant in case.applicants:
            if applicant.credit_score < self.MINIMUM_CREDIT_SCORE:
                return False, None, "Poor credit score impacts eligibility."

        # Estimated premium fee (based on risk factors, age, and violations)
        base_premium = 1000
        premium_multiplier = 1.0

        if age < 25:
            premium_multiplier += 0.2
        if overall_minor_violations >= 3:
            premium_multiplier += overall_minor_violations * 0.05
        for applicant in case.applicants:
            if applicant.credit_score < self.CREDIT_SCORE_FEE_THRESHOLD:
                premium_multiplier += 0.1

        premium_fee = base_premium * premium_multiplier

        return True, round(premium_fee, 2), ""


class TestCarInsuranceCompliance(unittest.TestCase):

    def setUp(self):
        self.compliance = CarInsurancePolicy()
        self.today = date.today()

    def create_applicant(self, age, license_status="valid", issue_date=None, issue_country="us", driving_history=None,
                         insurance_history=None, credit_score=700, is_primary_holder=True):
        birth_date = self.today - timedelta(days=age * 365)
        license_issue_date = issue_date or (self.today - timedelta(days=365 * 5))

        driving_license = DrivingLicense(
            status=license_status,
            issue_date=license_issue_date,
            expiration_date=self.today + timedelta(days=365 * 5),
            issue_country=issue_country
        )

        return Applicant(
            birth_date=birth_date,
            driving_license=driving_license,
            driving_history=driving_history or [],
            history_insurance_coverage=insurance_history or [],
            address={"country": "us", "state": "california"},
            credit_score=credit_score,
            is_primary_holder=is_primary_holder
        )

    def create_vehicle(self, owner, age, use="personal", passed_inspection=True):
        vehicle_date_creation = self.today - timedelta(days=age * 365)
        return Vehicle(
            registered_on=owner,
            vehicle_use=use,
            passed_safety_inspections=passed_inspection,
            date_creation=vehicle_date_creation
        )

    def test_primary_applicant_under_18(self):
        applicant = self.create_applicant(17, is_primary_holder=True)
        vehicle = self.create_vehicle(applicant, 5)
        request = CarInsuranceRequest([applicant], vehicle, 50000, 25000)
        eligible, premium, reason = self.compliance.test_eligibility(request)
        self.assertFalse(eligible)
        self.assertEqual(reason, "Primary policyholder must be at least 18 years old.")

    def test_primary_applicant_over_75(self):
        applicant = self.create_applicant(76, is_primary_holder=True)
        vehicle = self.create_vehicle(applicant, 5)
        request = CarInsuranceRequest([applicant], vehicle, 50000, 25000)
        eligible, premium, reason = self.compliance.test_eligibility(request)
        self.assertFalse(eligible)
        self.assertEqual(reason, "Applicants over 75 may require additional medical assessments.")

    def test_invalid_drivers_license(self):
        applicant = self.create_applicant(30, license_status="suspended", is_primary_holder=True)
        vehicle = self.create_vehicle(applicant, 5)
        request = CarInsuranceRequest([applicant], vehicle, 50000, 25000)
        eligible, premium, reason = self.compliance.test_eligibility(request)
        self.assertFalse(eligible)
        self.assertEqual(reason, "All applicants must have a valid driver’s license.")

    def test_international_driver_without_history(self):
        applicant = self.create_applicant(30, issue_country="france", driving_history=[])
        vehicle = self.create_vehicle(applicant, 5)
        request = CarInsuranceRequest([applicant], vehicle, 50000, 25000)
        eligible, premium, reason = self.compliance.test_eligibility(request)
        self.assertFalse(eligible)
        self.assertEqual(reason,
                         "International drivers must provide additional documentation or proof of driving history.")

    def test_vehicle_not_registered_to_applicant(self):
        owner = self.create_applicant(40, is_primary_holder=False)
        applicant = self.create_applicant(30, is_primary_holder=True)
        vehicle = self.create_vehicle(owner, 5)
        request = CarInsuranceRequest([applicant], vehicle, 50000, 25000)
        eligible, premium, reason = self.compliance.test_eligibility(request)
        self.assertFalse(eligible)
        self.assertEqual(reason,
                         "The vehicle must be registered in the name of the applicant or an immediate family member.")

    def test_commercial_vehicle_use(self):
        applicant = self.create_applicant(30, is_primary_holder=True)
        vehicle = self.create_vehicle(applicant, 5, use="commercial")
        request = CarInsuranceRequest([applicant], vehicle, 50000, 25000)
        eligible, premium, reason = self.compliance.test_eligibility(request)
        self.assertFalse(eligible)
        self.assertEqual(reason, "The vehicle must be used primarily for personal use.")

    def test_vehicle_older_than_20_years(self):
        applicant = self.create_applicant(30, is_primary_holder=True)
        vehicle = self.create_vehicle(applicant, 21)
        request = CarInsuranceRequest([applicant], vehicle, 50000, 25000)
        eligible, premium, reason = self.compliance.test_eligibility(request)
        self.assertFalse(eligible)
        self.assertEqual(reason, "The vehicle older than 20 years cannot be covered")

    def test_major_violation_disqualifies_applicant(self):
        history = [{"date": (self.today - timedelta(days=500)).isoformat(), "type": "DUI"}]
        applicant = self.create_applicant(30, driving_history=history, is_primary_holder=True)
        vehicle = self.create_vehicle(applicant, 5)
        request = CarInsuranceRequest([applicant], vehicle, 50000, 25000)
        eligible, premium, reason = self.compliance.test_eligibility(request)
        self.assertFalse(eligible)
        self.assertEqual(reason, "Major violations impact eligibility.")

    def test_multiple_minor_violations_disqualify(self):
        history = [{"date": (self.today - timedelta(days=400)).isoformat(), "type": "speeding"} for _ in range(3)]
        applicant = self.create_applicant(30, driving_history=history, is_primary_holder=True)
        vehicle = self.create_vehicle(applicant, 5)
        request = CarInsuranceRequest([applicant], vehicle, 50000, 25000)
        eligible, premium, reason = self.compliance.test_eligibility(request)
        self.assertFalse(eligible)
        self.assertEqual(reason, "Too many minor violations in the last five years.")

    def test_poor_credit_score_disqualifies(self):
        applicant = self.create_applicant(30, credit_score=400, is_primary_holder=True)
        vehicle = self.create_vehicle(applicant, 5)
        request = CarInsuranceRequest([applicant], vehicle, 50000, 25000)
        eligible, premium, reason = self.compliance.test_eligibility(request)
        self.assertFalse(eligible)
        self.assertEqual(reason, "Poor credit score impacts eligibility.")

    # test many applicants:
    def test_non_primary_holder_can_own_vehicle(self):
        primary_applicant = self.create_applicant(30, is_primary_holder=True)
        second = self.create_applicant(60)
        vehicle = self.create_vehicle(second, 5)
        case = CarInsuranceRequest([primary_applicant, second], vehicle, 50000, 30000)
        result, _, message = self.compliance.test_eligibility(case)
        self.assertTrue(result)

    # test many applicants:
    def test_vehicle_not_registered_to_applicant_or_family(self):
        primary_applicant = self.create_applicant(30, is_primary_holder=True)
        family_member = self.create_applicant(60)
        vehicle = self.create_vehicle(family_member, 5)
        case = CarInsuranceRequest([primary_applicant], vehicle, 50000, 30000)
        result, _, message = self.compliance.test_eligibility(case)
        self.assertFalse(result)
        self.assertEqual(message, "The vehicle must be registered in the name of the applicant or an immediate family member.")

    def test_vehicle_must_be_registered_to_applicant_or_family(self):
        primary_applicant = self.create_applicant(30, is_primary_holder=True)
        unrelated_member = self.create_applicant(60)
        family_member = self.create_applicant(50)
        unrelated_member.family_members.append(family_member)
        family_member.family_members.append(unrelated_member)
        vehicle = self.create_vehicle(family_member, 5)

        case = CarInsuranceRequest([primary_applicant, unrelated_member], vehicle, 50000, 30000)
        result, _, message = self.compliance.test_eligibility(case)
        self.assertTrue(result)

    def test_multiple_applicants_one_with_bad_record(self):
        primary_applicant = self.create_applicant(30, is_primary_holder=True)
        bad_driver = self.create_applicant(40, driving_history=[
                                   {"type": "DUI", "date": (self.today - timedelta(days=365)).isoformat()}])
        vehicle = self.create_vehicle(primary_applicant, 5)
        case = CarInsuranceRequest([primary_applicant, bad_driver], vehicle, 50000, 30000)
        result, _, message = self.compliance.test_eligibility(case)
        self.assertFalse(result)
        self.assertEqual(message, "Major violations impact eligibility.")

    def test_multiple_applicants_valid_license_and_record(self):
        primary_applicant = self.create_applicant(30, is_primary_holder=True)
        secondary_applicant = self.create_applicant(40)
        vehicle = self.create_vehicle(primary_applicant, 5)
        case = CarInsuranceRequest([primary_applicant, secondary_applicant], vehicle, 50000, 30000)
        result, _, message = self.compliance.test_eligibility(case)
        self.assertTrue(result)

    def test_multiple_applicants_one_with_few_minor_violations(self):
        primary_applicant = self.create_applicant(30, is_primary_holder=True)
        minor_violation_driver = self.create_applicant(40, driving_history=[{"type": "Speeding",
                                                             "date": (self.today - timedelta(days=180)).isoformat()},
                                                            {"type": "Failure to Signal",
                                                             "date": (self.today - timedelta(days=300)).isoformat()}])
        vehicle = self.create_vehicle(primary_applicant, 5)
        case = CarInsuranceRequest([primary_applicant, minor_violation_driver], vehicle, 50000,
                                   30000)
        result, _, message = self.compliance.test_eligibility(case)
        self.assertTrue(result)

    def test_multiple_applicants_one_with_many_minor_violations_last_five_years(self):
        primary_applicant = self.create_applicant(30, is_primary_holder=True)
        bad_driver = self.create_applicant(40, driving_history=[
                                   {"type": "Speeding", "date": (self.today - timedelta(days=180)).isoformat()},
                                   {"type": "Failure to Signal",
                                    "date": (self.today - timedelta(days=300)).isoformat()},
                                   {"type": "Reckless Driving", "date": (self.today - timedelta(days=600)).isoformat()},
                                   {"type": "Running a Red Light",
                                    "date": (self.today - timedelta(days=900)).isoformat()}])
        vehicle = self.create_vehicle(primary_applicant, 5)

        case = CarInsuranceRequest([primary_applicant, bad_driver], vehicle, 50000, 30000)
        result, _, message = self.compliance.test_eligibility(case)
        self.assertFalse(result)
        self.assertEqual(message, "Too many minor violations in the last five years.")

    def test_multiple_applicants_one_with_many_old_minor_violations(self):
        primary_applicant = self.create_applicant(30, is_primary_holder=True)
        past_violation_driver = self.create_applicant(40, driving_history=[{"type": "Speeding",
                                                            "date": (self.today - timedelta(days=2200)).isoformat()},
                                                           {"type": "Failure to Signal",
                                                            "date": (self.today - timedelta(days=2300)).isoformat()},
                                                           {"type": "Reckless Driving",
                                                            "date": (self.today - timedelta(days=2400)).isoformat()}])
        vehicle = self.create_vehicle(primary_applicant, 5)

        case = CarInsuranceRequest([primary_applicant, past_violation_driver], vehicle, 50000, 30000)
        result, _, message = self.compliance.test_eligibility(case)
        self.assertTrue(result)

    # Fees tests:
    def test_fee_for_young_driver(self):
        applicant = self.create_applicant(20, is_primary_holder=True, credit_score=700)
        vehicle = self.create_vehicle(applicant, 5)
        case = CarInsuranceRequest([applicant], vehicle, 50000, 30000)
        result, fee, _ = self.compliance.test_eligibility(case)
        self.assertTrue(result)
        self.assertGreater(fee, 1000)

    def test_fee_for_low_credit_score(self):
        applicant = self.create_applicant(30, is_primary_holder=True, credit_score=600)
        vehicle = self.create_vehicle(applicant, 5)
        case = CarInsuranceRequest([applicant], vehicle, 50000, 30000)
        result, fee, _ = self.compliance.test_eligibility(case)
        self.assertTrue(result)
        self.assertEqual(fee, 1100)

    def test_fee_for_multiple_minor_violations(self):
        applicant1 = self.create_applicant(40, is_primary_holder=True, driving_history=[
                                  {"type": "Speeding", "date": (self.today - timedelta(days=180)).isoformat()},
                                  {"type": "Failure to Signal", "date": (self.today - timedelta(days=300)).isoformat()}])

        applicant2 = self.create_applicant(40, driving_history=[
                                  {"type": "Running a Stop Sign",
                                   "date": (self.today - timedelta(days=600)).isoformat()}])

        vehicle = self.create_vehicle(applicant1, 5)

        case = CarInsuranceRequest([applicant1, applicant2], vehicle, 50000, 30000)
        result, fee, _ = self.compliance.test_eligibility(case)
        self.assertTrue(result)
        self.assertEqual(fee, 1150)


if __name__ == "__main__":
    unittest.main()

import sys
import os
from typing import Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from common.generic_policy import Compliance


class CarInsuranceCompliance(Compliance):
    """
    Implementation of the Compliance abstract class to assess eligibility for car insurance
    based on predefined policy criteria.
    """

    def test_eligibility(self, case: dict) -> Tuple[bool, float, str]:
        """
        Evaluates an applicant's eligibility for car insurance based on the provided case details.

        Args:
            case (dict): Contains applicant and vehicle details.

        Returns:
            Tuple[bool, float, str]:
                - Eligibility status (True/False)
                - Suggested premium fee (float, 0.0 if ineligible)
                - Error message (empty if eligible, otherwise reason for ineligibility)
        """

        # Applicant Age Requirements
        age = case.get("age", 0)
        if age < 18:
            return False, 0.0, "Primary policyholder must be at least 18 years old."
        if age > 75:
            return False, 0.0, "Drivers over 75 may require additional medical assessments."

        # Valid Driver’s License
        license_status = case.get("license_status", "invalid")
        if license_status not in ["valid", "international"]:
            return False, 0.0, "Driver must hold a valid driver’s license."

        # Vehicle Eligibility
        if not case.get("vehicle_registered", False):
            return False, 0.0, "Vehicle must be registered under applicant or immediate family."
        if case.get("vehicle_use", "personal") != "personal":
            return False, 0.0, "Vehicle used for commercial purposes requires different policy."
        if case.get("vehicle_age", 0) > 20:
            return False, 0.0, "Vehicles older than 20 years may not be covered."

        # Driving Record Requirements
        major_violations = case.get("major_violations", 0)
        minor_violations = case.get("minor_violations", 0)

        if major_violations > 0 or minor_violations > 3:
            return False, 0.0, "Driving record does not meet eligibility criteria."

        # Insurance History
        if case.get("insurance_lapse", False):
            return False, 0.0, "History of insurance lapse impacts eligibility."

        # Residency & Vehicle Location
        if not case.get("residency_valid", False):
            return False, 0.0, "Applicant must reside in the policy's coverage region."

        # Credit Score (if applicable)
        credit_score = case.get("credit_score", 700)
        if credit_score < 500:
            return False, 0.0, "Poor credit score impacts eligibility."

        # Minimum Insurance Requirements
        if case.get("liability_coverage", 0) < case.get("state_min_liability", 0):
            return False, 0.0, "Applicant must purchase at least the minimum liability coverage."

        # Estimated premium fee (based on risk factors, age, and violations)
        base_premium = 1000
        premium_multiplier = 1.0

        if age < 25:
            premium_multiplier += 0.2
        if minor_violations > 0:
            premium_multiplier += minor_violations * 0.05
        if credit_score < 650:
            premium_multiplier += 0.1

        premium_fee = base_premium * premium_multiplier

        return True, premium_fee, ""


# Unit Test Class
import unittest


class TestCarInsurancePolicy(unittest.TestCase):
    """
    Unit test class for CarInsurancePolicy eligibility assessment.
    """

    def setUp(self):
        self.policy = CarInsuranceCompliance()

    def test_valid_application(self):
        case = {
            "age": 30,
            "license_status": "valid",
            "vehicle_registered": True,
            "vehicle_use": "personal",
            "vehicle_age": 10,
            "major_violations": 0,
            "minor_violations": 1,
            "insurance_lapse": False,
            "residency_valid": True,
            "credit_score": 700,
            "liability_coverage": 50000,
            "state_min_liability": 25000,
        }
        eligible, premium, error = self.policy.test_eligibility(case)
        self.assertTrue(eligible)
        self.assertGreater(premium, 0)
        self.assertEqual(error, "")

    def test_underage_applicant(self):
        case = {"age": 17}
        eligible, premium, error = self.policy.test_eligibility(case)
        self.assertFalse(eligible)
        self.assertEqual(premium, 0.0)
        self.assertEqual(error, "Primary policyholder must be at least 18 years old.")

    def test_invalid_license(self):
        case = {"age": 30, "license_status": "expired"}
        eligible, premium, error = self.policy.test_eligibility(case)
        self.assertFalse(eligible)
        self.assertEqual(error, "Driver must hold a valid driver’s license.")

    def test_vehicle_too_old(self):
        case = {"age": 30, "license_status": "valid", "vehicle_registered": True, "residency_valid": True, "vehicle_age": 25}
        eligible, premium, error = self.policy.test_eligibility(case)
        self.assertFalse(eligible)
        self.assertEqual(error, "Vehicles older than 20 years may not be covered.")

    def test_major_violation(self):
        case = {"age": 30, "license_status": "valid", "vehicle_registered": True, "residency_valid": True, "major_violations": 1}
        eligible, premium, error = self.policy.test_eligibility(case)
        self.assertFalse(eligible)
        self.assertEqual(error, "Driving record does not meet eligibility criteria.")

    def test_low_credit_score(self):
        case = {"age": 30, "license_status": "valid", "vehicle_registered": True, "residency_valid": True, "credit_score": 450}
        eligible, premium, error = self.policy.test_eligibility(case)
        self.assertFalse(eligible)
        self.assertEqual(error, "Poor credit score impacts eligibility.")


if __name__ == "__main__":
    unittest.main()

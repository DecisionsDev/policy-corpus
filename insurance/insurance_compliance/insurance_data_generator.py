import sys
import os
import random
from datetime import date, timedelta
import pandas as pd
from typing import List, Dict, Tuple

from insurance.insurance_compliance.insurance_policy import CarInsurancePolicy

# Append the path to import the abstract class and compliance checker
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_data_generator import DataGenerator
from insurance.insurance_compliance.insurance_request import CarInsuranceRequest, Vehicle, Applicant, DrivingLicense

class CarInsuranceDataGenerator(DataGenerator):

    COLUMN_NAMES = [
            "applicants", "vehicle", "liability_coverage", "state_min_liability",
            "eligible", "premium_fee", "reason"
        ]

    EVAL_COLUMN_NAMES = ["eligible", "premium_fee", "reason"]

    def __init__(self):
        super().__init__(CarInsurancePolicy())

    def generate_eligible_case(self) -> Dict:
        today = date.today()
        num_applicants = random.randint(1, 3)
        applicants = []

        for _ in range(num_applicants):
            birth_date = today - timedelta(days=365*random.randint(18, 74))  # Age between 18 and 74
            issue_date = today - timedelta(days=365*random.randint(1, 20))  # Issued 1 to 20 years ago
            expiration_date = issue_date + timedelta(days=365*5)  # Expires in 5 years
            credit_score = random.randint(500, 850)  # Credit score between 500 and 850

            driving_history = []
            if random.random() < 0.5:  # 50% chance to add minor violations
                for _ in range(random.randint(1, 2)):
                    violation_date = today - timedelta(days=365*random.randint(6, 10))  # Old violations
                    driving_history.append({"type": "minor", "date": violation_date.isoformat()})

            applicant = Applicant(
                birth_date=birth_date,
                driving_license=DrivingLicense(
                    status="valid",
                    issue_date=issue_date,
                    expiration_date=expiration_date,
                    issue_country="us"
                ),
                family_members=[],
                driving_history=driving_history,
                history_insurance_coverage=[{"lapse": False, "fraud": False, "claims": random.randint(0, 2), "cancellation_reason": None}],
                address={"country": "us", "state": random.choice(["california", "texas", "florida", "ohio"])},
                is_primary_holder=(_ == 0),  # First applicant is the primary holder
                credit_score=credit_score
            )
            applicants.append(applicant)

        vehicle = Vehicle(
            registered_on=applicants[0],
            vehicle_use="personal",
            passed_safety_inspections=True,
            date_creation=today - timedelta(days=365*random.randint(1, 20)),  # 1 to 20 years old
            vehicle_type="normal"
        )

        case = CarInsuranceRequest(
            applicants=applicants,
            vehicle=vehicle,
            liability_coverage=random.randint(50000, 200000),
            state_min_liability=50000
        )

        eligible, premium_fee, reason = self.determine_eligibility(case)
        csv = case.to_dict()
        csv["eligible"] = eligible
        csv["premium_fee"] = premium_fee
        csv["reason"] = reason

        return csv

    def generate_non_eligible_case(self) -> Dict:
        today = date.today()
        reason_type = random.choice([
            "no_primary_applicant",
            "age_too_young",
            "age_too_old",
            "invalid_license",
            "future_issue_date",
            "international_driver",
            "vehicle_not_registered",
            "commercial_use",
            "failed_safety_inspections",
            "vehicle_too_old",
            "major_violations",
            "too_many_minor_violations",
            "recent_license_suspensions",
            "insurance_lapses",
            "insurance_fraud",
            "too_many_claims",
            "non_payment_cancellation",
            "invalid_address",
            "low_liability_coverage",
            "poor_credit_score"
        ])

        num_applicants = random.randint(1, 3)
        applicants = []

        for _ in range(num_applicants):
            birth_date = today - timedelta(days=365 * random.randint(18, 74))  # Age between 18 and 74
            issue_date = today - timedelta(days=365 * random.randint(1, 20))  # Issued 1 to 20 years ago
            expiration_date = issue_date + timedelta(days=365 * 5)  # Expires in 5 years
            credit_score = random.randint(500, 850)  # Credit score between 500 and 850

            driving_history = []
            if random.random() < 0.5:  # 50% chance to add minor violations
                for _ in range(random.randint(1, 2)):
                    violation_date = today - timedelta(days=365 * random.randint(6, 10))  # Old violations
                    driving_history.append({"type": "minor", "date": violation_date.isoformat()})

            applicant = Applicant(
                birth_date=birth_date,
                driving_license=DrivingLicense(
                    status="valid",
                    issue_date=issue_date,
                    expiration_date=expiration_date,
                    issue_country="us"
                ),
                family_members=[],
                driving_history=driving_history,
                history_insurance_coverage=[
                    {"lapse": False, "fraud": False, "claims": random.randint(0, 2), "cancellation_reason": None}],
                address={"country": "us", "state": random.choice(["california", "texas", "florida", "ohio"])},
                is_primary_holder=(_ == 0),  # First applicant is the primary holder
                credit_score=credit_score
            )
            applicants.append(applicant)

        vehicle = Vehicle(
            registered_on=applicants[0],
            vehicle_use="personal",
            passed_safety_inspections=True,
            date_creation=today - timedelta(days=365 * random.randint(1, 20)),  # 1 to 20 years old
            vehicle_type="normal"
        )

        if reason_type == "no_primary_applicant":
            for applicant in applicants:
                applicant.is_primary_holder = False
        elif reason_type == "age_too_young":
            applicants[0].birth_date = today - timedelta(days=365 * 17)  # Age 17
        elif reason_type == "age_too_old":
            applicants[0].birth_date = today - timedelta(days=365 * 76)  # Age 76
        elif reason_type == "invalid_license":
            applicants[0].driving_license.status = "invalid"
        elif reason_type == "future_issue_date":
            applicants[0].driving_license.issue_date = today + timedelta(days=1)  # Issued in the future
        elif reason_type == "international_driver":
            applicants[0].driving_license.issue_country = "canada"
        elif reason_type == "vehicle_not_registered":
            vehicle.registered_on = Applicant()  # Not registered to any applicant
        elif reason_type == "commercial_use":
            vehicle.vehicle_use = "commercial"
        elif reason_type == "failed_safety_inspections":
            vehicle.passed_safety_inspections = False
        elif reason_type == "vehicle_too_old":
            vehicle.date_creation = today - timedelta(days=365 * 21)  # 21 years old
        elif reason_type == "major_violations":
            applicants[0].driving_history.append({"type": "DUI", "date": (today - timedelta(days=365)).isoformat()})
        elif reason_type == "too_many_minor_violations":
            for _ in range(3):
                violation_date = today - timedelta(days=365 * random.randint(1, 5))  # Recent violations
                applicants[0].driving_history.append({"type": "minor", "date": violation_date.isoformat()})
        elif reason_type == "recent_license_suspensions":
            applicants[0].driving_license.status_history.append(
                {"status": "suspended", "date": (today - timedelta(days=365)).isoformat()})
        elif reason_type == "insurance_lapses":
            applicants[0].history_insurance_coverage[0]["lapse"] = True
        elif reason_type == "insurance_fraud":
            applicants[0].history_insurance_coverage[0]["fraud"] = True
        elif reason_type == "too_many_claims":
            applicants[0].history_insurance_coverage[0]["claims"] = 4
        elif reason_type == "non_payment_cancellation":
            applicants[0].history_insurance_coverage[0]["cancellation_reason"] = "non-payment"
        elif reason_type == "invalid_address":
            applicants[0].address = {"country": "canada", "state": "ontario"}
        elif reason_type == "low_liability_coverage":
            liability_coverage = 49999
        elif reason_type == "poor_credit_score":
            applicants[0].credit_score = 499

        case = CarInsuranceRequest(
            applicants=applicants,
            vehicle=vehicle,
            liability_coverage=random.randint(50000,
                                              200000) if reason_type != "low_liability_coverage" else liability_coverage,
            state_min_liability=50000
        )

        eligible, premium_fee, reason = self.determine_eligibility(case)

        csv = case.to_dict()
        csv["eligible"] = eligible
        csv["premium_fee"] = premium_fee
        csv["reason"] = reason

        return csv


from common.generic_data_generator import format_data_units

# paste this in the end of {policy_name}_data_generator.py file
if __name__ == "__main__":
    sizes = [100, 1000]
    generator = CarInsuranceDataGenerator()

    for size in sizes:
        df = generator.generate_test_dataset(size)
        data_units = format_data_units(size)
        df.to_csv(f'insurance_test_dataset_{data_units}.csv', index=False)
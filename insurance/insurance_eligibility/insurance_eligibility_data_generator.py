import random
import sys
import os
import pandas as pd
from typing import List, Dict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_data_generator import DataGenerator
from insurance_eligibility_compliance import CarInsuranceCompliance


class CarInsuranceDataGenerator(DataGenerator):
    COLUMN_NAMES = [
        "age", "license_status", "vehicle_registered", "vehicle_use", "vehicle_age",
        "major_violations", "minor_violations", "insurance_lapse", "residency_valid",
        "credit_score", "liability_coverage", "state_min_liability",
        "eligible", "premium_fee", "error_message"
    ]

    EVAL_COLUMN_NAMES = ["eligible", "premium_fee", "error_message"]

    def __init__(self):
        super().__init__(CarInsuranceCompliance())

    def generate_eligible_case(self) -> Dict:
        case = {
            "age": random.randint(18, 75),
            "license_status": random.choice(["valid", "international"]),
            "vehicle_registered": True,
            "vehicle_use": "personal",
            "vehicle_age": random.randint(0, 20),
            "major_violations": 0,
            "minor_violations": random.randint(0, 3),
            "insurance_lapse": False,
            "residency_valid": True,
            "credit_score": random.randint(500, 850),
            "liability_coverage": random.randint(50000, 200000),
            "state_min_liability": random.randint(10000, 50000)
        }
        eligibility_result = self.determine_eligibility(case)
        case.update({
            "eligible": eligibility_result[0],
            "premium_fee": eligibility_result[1],
            "error_message": eligibility_result[2]
        })
        return case

    def generate_non_eligible_case(self) -> Dict:
        case = {
            "age": random.choice([random.randint(0, 17), random.randint(76, 100)]),
            "license_status": random.choice(["expired", "revoked", "invalid"]),
            "vehicle_registered": random.choice([True, False]),
            "vehicle_use": random.choice(["commercial", "rental"]),
            "vehicle_age": random.randint(21, 30),
            "major_violations": random.randint(1, 5),
            "minor_violations": random.randint(4, 10),
            "insurance_lapse": True,
            "residency_valid": False,
            "credit_score": random.randint(300, 499),
            "liability_coverage": random.randint(0, 9000),
            "state_min_liability": random.randint(10000, 50000)
        }
        eligibility_result = self.determine_eligibility(case)
        case.update({
            "eligible": eligibility_result[0],
            "premium_fee": eligibility_result[1],
            "error_message": eligibility_result[2]
        })
        return case


from common.generic_data_generator import format_data_units

# paste this in the end of {policy_name}_data_generator.py file
if __name__ == "__main__":
    sizes = [100, 1000]
    generator = CarInsuranceDataGenerator()

    for size in sizes:
        df = generator.generate_test_dataset(size)
        data_units = format_data_units(size)
        df.to_csv(f'insurance_test_dataset_{data_units}.csv', index=False)
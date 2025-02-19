import sys
import os
import random
import pandas as pd
from typing import List, Dict, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_data_generator import DataGenerator, format_data_units
from loan_compliance import LoanApprovalCompliance


class LoanDataGenerator(DataGenerator):
    ################# CONSTANT PROPERTIES #################
    COLUMN_NAMES = [
        "age", "residency", "credit_score", "income", "employment_status",
        "financial_records", "dti", "loan_amount", "co_signer",
        "eligibility", "interest_rate", "message"
    ]

    EVAL_COLUMN_NAMES = ["eligibility", "interest_rate", "message"]

    def __init__(self):
        super().__init__(LoanApprovalCompliance())

    def generate_eligible_case(self) -> Dict:
        """
        Generates a case that meets all eligibility requirements.
        """
        case = {
            "age": random.randint(18, 65),
            "residency": "US",
            "credit_score": random.choice([600, 650, 700, 750, 800]),
            "income": random.randint(30000, 150000),
            "employment_status": random.choice(["employed", "self-employed"]),
            "financial_records": True if random.choice([True, False]) else False,
            "dti": round(random.uniform(0.1, 0.39), 2),
            "loan_amount": random.randint(5000, 50000),
            "co_signer": None if random.randint(1, 10) > 3 else {"credit_score": random.randint(600, 800)}
        }

        eligibility, interest_rate, message = super().determine_eligibility(case)
        case.update({"eligibility": eligibility, "interest_rate": interest_rate, "message": message})
        return case

    def generate_non_eligible_case(self) -> Dict:
        """
        Generates a case that violates at least one eligibility criterion.
        """
        case = {
            "age": random.choice([16, 17, 66, 75]),  # Below or above acceptable age range
            "residency": random.choice(["Canada", "Mexico", "UK"]),
            "credit_score": random.choice([400, 500, 550]),  # Below required score
            "income": random.choice([10000, 20000, 29000]),  # Below required income
            "employment_status": random.choice(["unemployed", "self-employed"]),
            "financial_records": False,  # Required if self-employed
            "dti": round(random.uniform(0.41, 0.8), 2),  # Above max allowed ratio
            "loan_amount": random.choice([1000, 60000]),  # Out of range loan amounts
            "co_signer": None if random.randint(1, 10) > 5 else {"credit_score": random.randint(400, 550)}
        }

        eligibility, interest_rate, message = super().determine_eligibility(case)
        case.update({"eligibility": eligibility, "interest_rate": interest_rate, "message": message})
        return case


if __name__ == "__main__":
    sizes = [100, 1000]
    generator = LoanDataGenerator()

    for size in sizes:
        df = generator.generate_test_dataset(size)
        data_units = format_data_units(size)
        df.to_csv(f'loan_policy_test_dataset_{data_units}.csv', index=False)

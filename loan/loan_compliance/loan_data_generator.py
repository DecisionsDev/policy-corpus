import sys
import os
import random
from datetime import date, timedelta
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_data_generator import DataGenerator, format_data_units
from loan_policy import LoanApprovalPolicy
from loan.loan_compliance.loan_request import LoanRequest, Applicant


class LoanDataGenerator(DataGenerator):

    COLUMN_NAMES = ["applicant", "co_signer", "loan_amount", "eligibility", "interest_rate", "reason"]
    EVAL_COLUMN_NAMES = ["eligibility", "interest_rate", "reason"]

    def __init__(self):
        super().__init__(LoanApprovalPolicy())

    def generate_applicant(self, is_co_signer=False, eligible=False) -> Applicant:
        """Generate an applicant or co-signer with randomized values."""

        random_employment_status=random.choice(["full-time", "part-time", "self-employed"])
        return Applicant(
            birth_date=date.today() - timedelta(days=random.randint(18 if not eligible else 10, 40) * 365),
            address={"country": random.choice(["US", "Canada", "UK", "India"]) if is_co_signer else "US"},
            credit_score=random.randint(600, 850),
            annual_income=random.randint(30000, 150000),
            income_document=random.choice(["pay_stub", "bank_statement", "tax_return"]),
            employment_status=random_employment_status,
            is_financial_record_present=True,
            monthly_debt_amount=random.randint(0, 1000),
            monthly_gross_income=random.randint(1000, 20000),
        )

    def generate_eligible_case(self) -> dict:
        """Generate a fully eligible loan request."""
        applicant = self.generate_applicant(eligible=True)
        age = (date.today() - applicant.birth_date).days // 365
        if age < 18:
            co_signer = self.generate_applicant()
        else:
            co_signer = self.generate_applicant() if random.choice([True, False]) else None

        if applicant.employment_status == "self-employed":
            applicant.is_financial_record_present = True

        loan_request = LoanRequest(applicant, co_signer, random.randint(5000, 50000))
        eligibility, interest_rate, reason = self.determine_eligibility(loan_request.to_dict())

        return {
            "applicant": json.dumps(loan_request.applicant.to_dict()),
            "co_signer": json.dumps(loan_request.co_signer.to_dict()) if loan_request.co_signer else None,
            "loan_amount": loan_request.loan_amount,
            "eligibility": eligibility,
            "interest_rate": interest_rate,
            "reason": reason
        }

    def generate_non_eligible_case(self) -> dict:
        """Generate a non-eligible loan request with a randomized reason."""
        applicant = self.generate_applicant()
        co_signer = self.generate_applicant() if random.choice([True, False]) else None

        # Introduce various reasons for ineligibility
        failure_cases = [
            {"birth_date": date.today() - timedelta(days=random.randint(10, 17) * 365), "co_signer": None },  # Underage
            {"address": {"country": random.choice(["Canada", "UK", "India"])}, "co_signer": co_signer},  # Non-US resident
            {"credit_score": random.randint(300, 550), "co_signer": co_signer},  # Low credit score
            {"annual_income": random.randint(5000, 25000), "co_signer": co_signer},  # Low income
            {"income_document": None, "co_signer": co_signer},  # No income document
            {"employment_status": random.choice(["self-employed", "unemployed"]), "is_financial_record_present": False, "co_signer": co_signer},  # No financial records
            {"monthly_debt_amount": random.randint(3000, 7000), "monthly_gross_income": random.randint(6000, 9000), "co_signer": co_signer},  # High DTI
            {"loan_amount": random.randint(51000, 100000), "co_signer": co_signer},  # Loan amount exceeds limit
        ]

        failure_case = random.choice(failure_cases)
        for key, value in failure_case.items():
            setattr(applicant, key, value)
            co_signer = failure_case["co_signer"]

        loan_request = LoanRequest(applicant, co_signer, random.randint(5000, 100000))
        eligibility, interest_rate, reason = self.determine_eligibility(loan_request.to_dict())

        # csv = loan_request.to_dict()
        # csv["eligibility"] = eligibility
        # csv["interest_rate"] = interest_rate
        # csv["reason"] = reason

        return {
            "applicant": json.dumps(loan_request.applicant.to_dict()),
            "co_signer": json.dumps(loan_request.co_signer.to_dict()) if loan_request.co_signer else None,
            "loan_amount": loan_request.loan_amount,
            "eligibility": eligibility,
            "interest_rate": interest_rate,
            "reason": reason
        }
        # return csv


if __name__ == "__main__":
    sizes = [100, 1000]
    generator = LoanDataGenerator()

    for size in sizes:
        df = generator.generate_test_dataset(size)
        data_units = format_data_units(size)
        df.to_csv(f'loan_policy_test_dataset_{data_units}.csv', index=False, quoting=1, doublequote=True)

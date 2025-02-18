import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_policy import Policy


class LoanApprovalPolicy(Policy):
    MIN_AGE = 18
    MIN_CREDIT_SCORE = 600
    MIN_ANNUAL_INCOME = 30000
    MAX_DTI = 0.40
    MIN_LOAN_AMOUNT = 5000
    MAX_LOAN_AMOUNT = 50000

    def test_eligibility(self, info):
        if not self.meets_age_requirement(info['age']):
            return False, "Applicant does not meet the age requirement."
        if not self.meets_residency_requirement(info['residency']):
            return False, "Applicant does not meet the residency requirement."
        if not self.meets_credit_score_requirement(info['credit_score']):
            return False, "Applicant does not meet the credit score requirement."
        if not self.meets_income_requirement(info['annual_income']):
            return False, "Applicant does not meet the income requirement."
        if not self.meets_employment_status_requirement(info['employment_status'], info.get('financial_records')):
            return False, "Applicant does not meet the employment status requirement."
        if not self.meets_dti_requirement(info['annual_income'], info['dti']):
            return False, "Applicant does not meet the debt-to-income ratio requirement."
        if not self.meets_loan_amount_requirement(info['loan_amount']):
            return False, "Applicant does not meet the loan amount requirement."

        return True, "Applicant is eligible for the loan."

    def meets_age_requirement(self, age):
        return age >= self.MIN_AGE

    def meets_residency_requirement(self, residency):
        return residency.lower() in ["resident", "citizen"]

    def meets_credit_score_requirement(self, credit_score):
        return credit_score >= self.MIN_CREDIT_SCORE

    def meets_income_requirement(self, annual_income):
        return annual_income >= self.MIN_ANNUAL_INCOME

    def meets_employment_status_requirement(self, employment_status, financial_records):
        if employment_status.lower() == "self-employed":
            return financial_records is not None and len(financial_records) >= 2
        return employment_status.lower() in ["employed", "stable income"]

    def meets_dti_requirement(self, annual_income, monthly_debt):
        gross_monthly_income = annual_income / 12
        dti = monthly_debt / gross_monthly_income
        return dti <= self.MAX_DTI

    def meets_loan_amount_requirement(self, loan_amount):
        return self.MIN_LOAN_AMOUNT <= loan_amount <= self.MAX_LOAN_AMOUNT


if __name__ == "__main__":
    policy = LoanApprovalPolicy()

    applicant_info = {
        'age': 25,
        'residency': 'citizen',
        'credit_score': 650,
        'annual_income': 40000,
        'employment_status': 'employed',
        'monthly_debt': 1200,
        'loan_amount': 20000
    }

    eligible, reason = policy.test_eligibility(applicant_info)
    print(reason)


import sys
import os
from datetime import date, timedelta
from typing import Tuple

from loan.loan_compliance.loan_request import LoanRequest, Applicant

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.abstract_policy import Policy


class LoanApprovalPolicy(Policy):
    """
    Loan approval policy implementation based on Acme Car Insurance's lending criteria.
    """
    LOCAL_COUNTRIES_ABBREVIATIONS = ["us", "usa", "united states", "united states of america"]
    ACCEPTED_INCOME_PROOFS = ["pay_stub", "tax_return", "bank_statement"]

    def test_eligibility(self, case) -> Tuple[bool, float, str]:
        """
        Tests the eligibility of a loan applicant based on predefined criteria.
        """
        if not isinstance(case, LoanRequest):
            case = LoanRequest.from_dict(case)

        applicant = case.applicant
        co_signer = case.co_signer

        # Age Check
        age = (date.today() - applicant.birth_date).days // 365
        if age < 18:
            if not co_signer:
                return False, 0.0, "Applicant must be at least 18 years old or co-signer must be present."
            age_co_signer = (date.today() - co_signer.birth_date).days // 365
            if age_co_signer < 18:
                return False, 0.0, "Applicant must be at least 18 years old or co-signer must be at least 18 years old."

        # Residency Check
        if not applicant.address or str.lower(
                applicant.address.get("country")) not in self.LOCAL_COUNTRIES_ABBREVIATIONS:
            return False, 0.0, "Applicant must be a resident or citizen of the United States."

        # Credit Score Check
        if applicant.credit_score < 600:
            return False, 0.0, "Applicant must have a minimum credit score of 600."

        # Income Check
        if applicant.annual_income < 30000:
            return False, 0.0, "Applicant must have an annual income of at least $30,000."

        if not applicant.income_document or applicant.income_document not in self.ACCEPTED_INCOME_PROOFS:
            return False, 0.0, "Applicant must have an income document proof of at least $30,000."

        if applicant.employment_status == "unemployed":
            return False, 0.0, "Unemployed applicant cannot get the loan."

        # Employment Check
        if applicant.employment_status == "self-employed" and not applicant.is_financial_record_present:
            return False, 0.0, "Self-employed applicants must provide 2 years of financial records."

        # Debt-to-Income Ratio Check
        if applicant.calculate_dti() > 0.40:
            return False, 0.0, "Applicant's debt-to-income ratio must not exceed 40%."

        # Loan Amount Check
        if not (5000 <= case.loan_amount <= 50000):
            return False, 0.0, "Loan amount must be between $5,000 and $50,000."

        # Interest Rate Calculation
        # TODO Let it be like this ?
        interest_rate = max(5, min(15, 15 - ((applicant.credit_score - 600) / 100) * 2))

        # If all checks pass
        return True, interest_rate, f"Loan approved with {interest_rate:.2f}% APR."


import unittest


class TestLoanApprovalPolicy(unittest.TestCase):
    def setUp(self):
        self.policy = LoanApprovalPolicy()
        self.valid_applicant = Applicant(
            birth_date=date.today() - timedelta(days=30 * 365),
            address={"country": "US"},
            credit_score=700,
            annual_income=50000,
            income_document="pay_stub",
            employment_status="stable",
            is_financial_record_present=True,
            monthly_debt_amount=1000,
            monthly_gross_income=5000,
        )

    def test_loan_approved(self):
        loan_request = LoanRequest(self.valid_applicant, loan_amount=20000)
        result = self.policy.test_eligibility(loan_request)
        self.assertTrue(result[0])
        self.assertEqual(13, result[1])
        self.assertIn("Loan approved with", result[2])

    def test_underage_applicant(self):
        applicant = self.valid_applicant
        applicant.birth_date = date.today() - timedelta(days=17 * 365)
        loan_request = LoanRequest(applicant, loan_amount=20000)
        result = self.policy.test_eligibility(loan_request)
        self.assertEqual(result, (False, 0, "Applicant must be at least 18 years old or co-signer must be present."))

    def test_non_us_resident(self):
        applicant = self.valid_applicant
        applicant.address = {"country": "Canada"}
        loan_request = LoanRequest(applicant, loan_amount=20000)
        result = self.policy.test_eligibility(loan_request)
        self.assertEqual(result, (False, 0, "Applicant must be a resident or citizen of the United States."))

    def test_low_credit_score_no_cosigner(self):
        applicant = self.valid_applicant
        applicant.credit_score = 500
        loan_request = LoanRequest(applicant, loan_amount=20000)
        result = self.policy.test_eligibility(loan_request)
        self.assertEqual(result, (False, 0, "Applicant or co-signer must have a minimum credit score of 600."))

    def test_interest_rate_calculation(self):
        applicant = self.valid_applicant
        applicant.credit_score = 650
        loan_request = LoanRequest(applicant, loan_amount=20000)
        result = self.policy.test_eligibility(loan_request)
        self.assertIn("Loan approved with", result[2])

    def test_low_income(self):
        applicant = self.valid_applicant
        applicant.annual_income = 25000
        loan_request = LoanRequest(applicant, loan_amount=20000)
        result = self.policy.test_eligibility(loan_request)
        self.assertEqual(result, (False, 0.0, "Applicant must have an annual income of at least $30,000."))

    def test_high_dti(self):
        applicant = self.valid_applicant
        applicant.monthly_debt_amount = 3000
        loan_request = LoanRequest(applicant, loan_amount=20000)
        result = self.policy.test_eligibility(loan_request)
        self.assertEqual(result, (False, 0.0, "Applicant's debt-to-income ratio must not exceed 40%."))

    def test_invalid_loan_amount(self):
        loan_request = LoanRequest(self.valid_applicant, loan_amount=60000)
        result = self.policy.test_eligibility(loan_request)
        self.assertEqual(result, (False, 0, "Loan amount must be between $5,000 and $50,000."))

    def test_self_employed_missing_records(self):
        applicant = self.valid_applicant
        applicant.employment_status = "self-employed"
        applicant.is_financial_record_present = False
        loan_request = LoanRequest(applicant, loan_amount=20000)
        result = self.policy.test_eligibility(loan_request)
        self.assertEqual(result, (False, 0, "Self-employed applicants must provide 2 years of financial records."))

    def test_interest_rate_low_credit(self):
        applicant = self.valid_applicant
        applicant.credit_score = 600
        loan_request = LoanRequest(applicant, loan_amount=20000)
        result = self.policy.test_eligibility(loan_request)
        self.assertEqual(15, result[1])

    def test_interest_rate_high_credit(self):
        applicant = self.valid_applicant
        applicant.credit_score = 1200
        loan_request = LoanRequest(applicant, loan_amount=20000)
        result = self.policy.test_eligibility(loan_request)
        self.assertEqual(5, result[1])

    def test_interest_rate_mid_range(self):
        applicant = self.valid_applicant
        applicant.credit_score = 700
        loan_request = LoanRequest(applicant, loan_amount=20000)
        result = self.policy.test_eligibility(loan_request)
        self.assertEqual(13, result[1])


if __name__ == "__main__":
    unittest.main()

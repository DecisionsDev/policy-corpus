import sys
import os
from typing import Tuple

from common.abstract_policy import Policy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


class LoanApprovalPolicy(Policy):
    """
    Implementation of the Loan Approval Policy for Acme Car Insurance.
    This class evaluates loan applications based on eligibility criteria.
    """

    def test_eligibility(self, case: dict) -> Tuple[bool, float, str]:
        """
        Evaluates the eligibility of an applicant based on policy rules.

        Args:
            case (dict): A dictionary containing applicant details.

        Returns:
            Tuple[bool, float, str]:
                - Eligibility (bool): Whether the applicant is eligible.
                - Proposed Loan Interest Rate (float): Interest rate if approved, 0 otherwise.
                - Message (str): Approval details or rejection reason.
        """
        age = case.get("age", 0)
        residency = case.get("residency", "")
        credit_score = case.get("credit_score", 0)
        income = case.get("income", 0)
        employment_status = case.get("employment_status", "")
        financial_records = case.get("financial_records", False)
        dti = case.get("dti", 1.0)  # Debt-to-Income ratio
        loan_amount = case.get("loan_amount", 0)
        co_signer = case.get("co_signer", None)

        # Age check
        if age < 18:
            return False, 0, "Applicant must be at least 18 years old."

        # Residency check
        if residency.lower() != "us":
            return False, 0, "Applicant must be a resident or citizen of the United States."

        # Credit score check
        if credit_score < 600:
            if co_signer and co_signer.get("credit_score", 0) >= 600:
                pass  # Allowed with a co-signer
            else:
                return False, 0, "Credit score below 600. Applicant requires a co-signer."

        # Income check
        if income < 30000:
            return False, 0, "Minimum annual income of $30,000 is required."

        # Employment check
        if employment_status.lower() == "self-employed" and not financial_records:
            return False, 0, "Self-employed applicants must provide at least 2 years of financial records."

        # Debt-to-Income Ratio check
        if dti > 0.40:
            return False, 0, "Debt-to-Income ratio exceeds the maximum limit of 40%."

        # Loan amount check
        if loan_amount < 5000 or loan_amount > 50000:
            return False, 0, "Loan amount must be between $5,000 and $50,000."

        # Interest Rate Determination
        if credit_score >= 750:
            interest_rate = 5.0
        elif credit_score >= 700:
            interest_rate = 7.5
        elif credit_score >= 600:
            interest_rate = 10.0
        else:
            interest_rate = 15.0  # Worst-case scenario with co-signer

        return True, interest_rate, "Loan Approved. Interest Rate: {}%".format(interest_rate)


# Unit tests
import unittest


class TestLoanApprovalCompliance(unittest.TestCase):
    """Unit tests for LoanApprovalPolicy"""

    def setUp(self):
        self.policy = LoanApprovalPolicy()

    def test_valid_application(self):
        case = {
            "age": 30,
            "residency": "US",
            "credit_score": 720,
            "income": 50000,
            "employment_status": "employed",
            "dti": 0.30,
            "loan_amount": 20000
        }
        self.assertEqual(self.policy.test_eligibility(case), (True, 7.5, "Loan Approved. Interest Rate: 7.5%"))

    def test_underage_applicant(self):
        case = {"age": 17, "residency": "US"}
        self.assertEqual(self.policy.test_eligibility(case), (False, 0, "Applicant must be at least 18 years old."))

    def test_non_us_resident(self):
        case = {"age": 25, "residency": "Canada"}
        self.assertEqual(self.policy.test_eligibility(case),
                         (False, 0, "Applicant must be a resident or citizen of the United States."))

    def test_low_credit_score_without_cosigner(self):
        case = {"age": 25, "residency": "US", "credit_score": 550}
        self.assertEqual(self.policy.test_eligibility(case),
                         (False, 0, "Credit score below 600. Applicant requires a co-signer."))

    def test_low_credit_score_with_cosigner(self):
        case = {"age": 25, "residency": "US", "credit_score": 550, "co_signer": {"credit_score": 700}, "income": 50000, "dti": 0.30, "loan_amount": 20000}
        self.assertEqual(self.policy.test_eligibility(case), (True, 15.0, "Loan Approved. Interest Rate: 15.0%"))

    def test_low_income(self):
        case = {"age": 30, "residency": "US", "credit_score": 650, "income": 25000}
        self.assertEqual(self.policy.test_eligibility(case),
                         (False, 0, "Minimum annual income of $30,000 is required."))

    def test_high_dti(self):
        case = {"age": 35, "residency": "US", "credit_score": 700, "income": 60000, "dti": 0.45}
        self.assertEqual(self.policy.test_eligibility(case),
                         (False, 0, "Debt-to-Income ratio exceeds the maximum limit of 40%."))

    def test_out_of_range_loan_amount(self):
        case = {"age": 28, "residency": "US", "credit_score": 680, "income": 70000, "loan_amount": 60000, "dti": 0.4}
        self.assertEqual(self.policy.test_eligibility(case),
                         (False, 0, "Loan amount must be between $5,000 and $50,000."))


if __name__ == "__main__":
    unittest.main()

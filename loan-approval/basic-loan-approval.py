import math
from datetime import datetime, timedelta

# Loan approval policy implementation
class LoanApprovalPolicy:
    def __init__(self, applicant):
        self.applicant = applicant
        self.base_rate = self.applicant["base_rate"]  # Base interest rate in %
    
    def is_eligible(self):
        """Check if the applicant meets the basic eligibility criteria."""
        if not self.check_age():
            return False, "Applicant does not meet the age requirement."
        if self.applicant["credit_score"] < 600 or self.applicant["credit_score"] > 850:
            return False, "Applicant's credit score is outside the acceptable range."
        if self.applicant["annual_income"] < 30000:
            return False, "Applicant's annual income is below $30,000."
        if self.applicant["dti"] > 40:
            return False, "Applicant's debt-to-income ratio exceeds 40%."
        if self.applicant["loan_amount"] < 5000 or self.applicant["loan_amount"] > 50000:
            return False, "Loan amount must be between $5,000 and $50,000."
        return True, "Applicant is eligible."

    def check_age(self):
        """Check if the applicant is 18 years or older."""
        today = datetime.now()
        age = (today - self.applicant["birthdate"]).days // 365
        return age >= 18

    def calculate_interest_rate(self):
        """Calculate the final interest rate based on the applicant's information."""
        rate = self.base_rate

        # Credit Score Adjustment
        credit_score = self.applicant["credit_score"]
        if credit_score >= 750:
            rate += 0
        elif 700 <= credit_score < 750:
            rate += 1
        elif 650 <= credit_score < 700:
            rate += 2
        elif 600 <= credit_score < 650:
            rate += 3
        
        # Loan Amount Adjustment
        loan_amount = self.applicant["loan_amount"]
        if 10000 <= loan_amount <= 30000:
            rate += 0.5
        elif 30000 < loan_amount <= 50000:
            rate += 1

        # Loan Term Adjustment
        loan_term = self.applicant["loan_term"]
        if 25 <= loan_term <= 36:
            rate += 0.5
        elif 37 <= loan_term <= 48:
            rate += 1
        elif loan_term > 48:
            rate += 1.5
        
        return rate

    def calculate_monthly_repayment(self, principal, rate, term_months):
        """Calculate the monthly repayment using the amortization formula."""
        monthly_rate = rate / 100 / 12
        n = term_months
        if monthly_rate == 0:
            return principal / n
        else:
            return principal * monthly_rate * (1 + monthly_rate) ** n / ((1 + monthly_rate) ** n - 1)

    def process_application(self):
        """Process the loan application, calculate the interest rate and repayment if eligible."""
        eligible, message = self.is_eligible()
        if not eligible:
            return {"status": "rejected", "message": message}
        
        interest_rate = self.calculate_interest_rate()
        monthly_repayment = self.calculate_monthly_repayment(
            round(self.applicant["loan_amount"], 2), interest_rate, self.applicant["loan_term"]
        )
        
        return {
            "status": "approved",
            "interest_rate": interest_rate,
            "monthly_repayment": round(monthly_repayment, 2)
        }

# Test cases
def test_loan_application():
    # Test case for different interest rate categories
    
    # 1. Credit score >= 750, no rate increase for credit score
    applicant1 = {
        "birthdate": datetime.now() - timedelta(days=365 * 30),  # 30 years old
        "credit_score": 760,  # No credit score adjustment
        "annual_income": 60000,
        "loan_amount": 20000,  # No loan amount adjustment
        "loan_term": 24,  # No loan term adjustment
        "dti": 35,
        "base_rate": 5.0
    }

    # 2. Credit score between 700 and 749, +1% for credit score
    applicant2 = {
        "birthdate": datetime.now() - timedelta(days=365 * 40),  # 40 years old
        "credit_score": 720,  # +1% for credit score
        "annual_income": 60000,
        "loan_amount": 20000,  # No loan amount adjustment
        "loan_term": 36,  # +0.5% for loan term
        "dti": 35,
        "base_rate": 5.0
    }

    # 3. Credit score between 650 and 699, +2% for credit score
    applicant3 = {
        "birthdate": datetime.now() - timedelta(days=365 * 50),  # 50 years old
        "credit_score": 670,  # +2% for credit score
        "annual_income": 60000,
        "loan_amount": 30000,  # +0.5% for loan amount
        "loan_term": 48,  # +1% for loan term
        "dti": 35,
        "base_rate": 5.0
    }

    # 4. Credit score between 600 and 649, +3% for credit score
    applicant4 = {
        "birthdate": datetime.now() - timedelta(days=365 * 35),  # 35 years old
        "credit_score": 640,  # +3% for credit score
        "annual_income": 60000,
        "loan_amount": 45000,  # +1% for loan amount
        "loan_term": 60,  # +1.5% for loan term
        "dti": 35,
        "base_rate": 5.0
    }

    # 5. Loan term > 48 months, +1.5% for long loan term
    applicant5 = {
        "birthdate": datetime.now() - timedelta(days=365 * 45),  # 45 years old
        "credit_score": 750,  # No credit score adjustment
        "annual_income": 60000,
        "loan_amount": 40000,  # +1% for loan amount
        "loan_term": 60,  # +1.5% for loan term
        "dti": 35,
        "base_rate": 5.0
    }

    # 6. Applicant rejected due to credit score < 600
    applicant6 = {
        "birthdate": datetime.now() - timedelta(days=365 * 30),  # 30 years old
        "credit_score": 580,  # Below minimum credit score
        "annual_income": 60000,
        "loan_amount": 20000,
        "loan_term": 24,
        "dti": 35,
        "base_rate": 5.0
    }

    # 7. Applicant rejected due to income < $30,000
    applicant7 = {
        "birthdate": datetime.now() - timedelta(days=365 * 30),  # 30 years old
        "credit_score": 720,
        "annual_income": 25000,  # Below minimum income
        "loan_amount": 20000,
        "loan_term": 24,
        "dti": 35,
        "base_rate": 5.0
    }

    # 8. Applicant rejected due to DTI > 40%
    applicant8 = {
        "birthdate": datetime.now() - timedelta(days=365 * 30),  # 30 years old
        "credit_score": 720,
        "annual_income": 60000,
        "loan_amount": 20000,
        "loan_term": 24,
        "dti": 45,  # Above maximum DTI
        "base_rate": 5.0
    }

    # 9. Applicant rejected due to loan amount < $5,000
    applicant9 = {
        "birthdate": datetime.now() - timedelta(days=365 * 30),  # 30 years old
        "credit_score": 720,
        "annual_income": 60000,
        "loan_amount": 4000,  # Below minimum loan amount
        "loan_term": 24,
        "dti": 35,
        "base_rate": 5.0
    }

    # 10. Applicant rejected due to loan amount > $50,000
    applicant10 = {
        "birthdate": datetime.now() - timedelta(days=365 * 30),  # 30 years old
        "credit_score": 720,
        "annual_income": 60000,
        "loan_amount": 60000,  # Above maximum loan amount
        "loan_term": 24,
        "dti": 35,
        "base_rate": 5.0
    }

    # 11. Applicant rejected due to age < 18
    applicant11 = {
        "birthdate": datetime.now() - timedelta(days=365 * 17),  # 30 years old
        "credit_score": 720,
        "annual_income": 60000,
        "loan_amount": 6000,  # Above maximum loan amount
        "loan_term": 24,
        "dti": 35,
        "base_rate": 3.0
    }

    # 12. Base rate at zero
    applicant12 = {
        "birthdate": datetime.now() - timedelta(days=365 * 23),  # 30 years old
        "credit_score": 850,
        "annual_income": 60000,
        "loan_amount": 6000,  # Above maximum loan amount
        "loan_term": 24,
        "dti": 35,
        "base_rate": 0.0
    }

    # Process each test case
    applicants = [
        applicant1, applicant2, applicant3, applicant4, applicant5,
        applicant6, applicant7, applicant8, applicant9, applicant10,
        applicant11, applicant12
    ]
    
    for i, applicant in enumerate(applicants, start=1):
        policy = LoanApprovalPolicy(applicant)
        result = policy.process_application()
        print(f"Applicant {i} Result:", result)

if __name__ == "__main__":
    test_loan_application()

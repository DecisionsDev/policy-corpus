import json
from datetime import date
from typing import Dict


class Applicant:
    def __init__(self,
                 birth_date: date = None,
                 address: Dict = None,
                 credit_score: float = None,
                 annual_income: float = None,
                 income_document: str = None,
                 employment_status: str = None, # stable, self-employed
                 is_financial_record_present: bool = False,
                 monthly_debt_amount: float = None,
                 monthly_gross_income: float = None,
                 ):
        self.birth_date = birth_date
        self.address = address
        self.credit_score = credit_score
        self.annual_income = annual_income
        self.income_document = income_document
        self.employment_status = employment_status
        self.is_financial_record_present = is_financial_record_present
        self.monthly_debt_amount = monthly_debt_amount
        self.monthly_gross_income = monthly_gross_income

    def calculate_dti(self):
        return round(self.monthly_debt_amount / self.monthly_gross_income if self.monthly_debt_amount and self.monthly_gross_income else 0.0, 2)

    def to_dict(self) -> dict:
        return {
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "address": self.address,
            "credit_score": self.credit_score,
            "annual_income": self.annual_income,
            "income_document": self.income_document,
            "employment_status": self.employment_status,
            "is_financial_record_present": self.is_financial_record_present,
            "monthly_debt_amount": self.monthly_debt_amount,
            "monthly_gross_income": self.monthly_gross_income
        }

    @staticmethod
    def from_dict(data: dict):
        if not data:
            return None
        return Applicant(
            birth_date=date.fromisoformat(data["birth_date"]) if data.get("birth_date") else None,
            address=data.get("address", {}),
            credit_score=data.get("credit_score", None),
            annual_income=data.get("annual_income", None),
            income_document=data.get("income_document", None),
            employment_status=data.get("employment_status", "unemployed"),
            is_financial_record_present=data.get("is_financial_record_present", False),
            monthly_debt_amount=data.get("monthly_debt_amount", None),
            monthly_gross_income=data.get("monthly_gross_income", None)
        )

    def __eq__(self, other):
        if not isinstance(other, Applicant):
            return False
        return self.to_dict() == other.to_dict()

    def __hash__(self):
        return hash(self.to_dict())

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)


class LoanRequest:
    def __init__(self,
                applicant: Applicant,
                co_signer: Applicant = None,
                loan_amount: float = None):
        self.applicant = applicant
        self.co_signer = co_signer
        self.loan_amount = loan_amount

    def to_dict(self) -> dict:
        return {
            "applicant": self.applicant.to_dict(),
            "co_signer": self.co_signer.to_dict() if self.co_signer else None,
            "loan_amount": self.loan_amount
        }

    @staticmethod
    def from_dict(data: dict):
        return LoanRequest(
            applicant=Applicant.from_dict(json.loads(data["applicant"]) if isinstance(data["applicant"], str) else data["applicant"]),
            co_signer=Applicant.from_dict(json.loads(data["co_signer"]) if isinstance(data["co_signer"], str) and len(data["co_signer"]) > 0 else data["co_signer"]),
            loan_amount=float(data["loan_amount"])
        )

    def __eq__(self, other):
        if not isinstance(other, LoanRequest):
            return False
        return self.to_dict() == other.to_dict()

    def __hash__(self):
        return hash(self.to_dict())

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

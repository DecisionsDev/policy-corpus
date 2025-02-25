import json
import unittest
from datetime import date
from typing import List, Dict
import csv


class DrivingLicense:
    def __init__(self,
                 status: str = "invalid",
                 issue_date: date = None,
                 expiration_date: date = None,
                 status_history: List[Dict] = None,
                 issue_country: str = "us"):
        self.status = status
        self.issue_date = issue_date
        self.expiration_date = expiration_date
        self.status_history = status_history or []
        self.issue_country = issue_country

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "status_history": self.status_history,
            "issue_country": self.issue_country
        }

    @staticmethod
    def from_dict(data: dict):
        return DrivingLicense(
            status=data.get("status"),
            issue_date=date.fromisoformat(data["issue_date"]) if data.get("issue_date") else None,
            expiration_date=date.fromisoformat(data["expiration_date"]) if data.get("expiration_date") else None,
            status_history=data.get("status_history", []),
            issue_country=data.get("issue_country", "us")
        )

    @staticmethod
    def save_to_csv(filename: str, licenses: list):
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["status", "issue_date", "expiration_date", "status_history", "issue_country"])
            writer.writeheader()
            for license in licenses:
                writer.writerow(license.to_dict())

    @staticmethod
    def load_from_csv(filename: str) -> list:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            return [DrivingLicense.from_dict(row) for row in reader]

    def __eq__(self, other):
        if not isinstance(other, DrivingLicense):
            return False
        return (
                self.status == other.status and
                self.issue_date == other.issue_date and
                self.expiration_date == other.expiration_date and
                self.status_history == other.status_history and
                self.issue_country == other.issue_country
        )

    def __hash__(self):
        return hash((
            self.status,
            self.issue_date,
            self.expiration_date,
            tuple(tuple(d.items()) for d in self.status_history),
            self.issue_country
        ))

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)


class Applicant:
    def __init__(self,
                 birth_date: date = None,
                 driving_license: DrivingLicense = None,
                 family_members: List = None,
                 driving_history: List[Dict] = None,
                 history_insurance_coverage: List[Dict] = None,
                 address: Dict = None,
                 is_primary_holder: bool = False,
                 credit_score: float = None):
        self.birth_date = birth_date
        self.driving_license = driving_license or DrivingLicense()
        self.family_members = family_members or []
        self.driving_history = driving_history or []
        self.history_insurance_coverage = history_insurance_coverage or []
        self.address = address or {}
        self.is_primary_holder = is_primary_holder
        self.credit_score = credit_score

    def to_dict(self) -> dict:
        return {
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "driving_license": self.driving_license.to_dict(),
            "family_members": self.family_members,
            "driving_history": self.driving_history,
            "history_insurance_coverage": self.history_insurance_coverage,
            "address": self.address,
            "is_primary_holder": self.is_primary_holder,
            "credit_score": self.credit_score
        }

    @staticmethod
    def from_dict(data: dict):
        return Applicant(
            birth_date=date.fromisoformat(data["birth_date"]) if data.get("birth_date") else None,
            driving_license=DrivingLicense.from_dict(data["driving_license"]) if data.get("driving_license") else None,
            family_members=data.get("family_members", []),
            driving_history=data.get("driving_history", []),
            history_insurance_coverage=data.get("history_insurance_coverage", []),
            address=data.get("address", {}),
            is_primary_holder=data.get("is_primary_holder", False),
            credit_score=data.get("credit_score", None)
        )

    def __eq__(self, other):
        if not isinstance(other, Applicant):
            return False
        return (
                self.birth_date == other.birth_date and
                self.driving_license == other.driving_license and
                self.family_members == other.family_members and
                self.driving_history == other.driving_history and
                self.history_insurance_coverage == other.history_insurance_coverage and
                self.address == other.address and
                self.is_primary_holder == other.is_primary_holder and
                self.credit_score == other.credit_score
        )

    def __hash__(self):
        return hash((
            self.birth_date,
            self.driving_license,
            tuple(self.family_members),
            tuple(tuple(d.items()) for d in self.driving_history),
            tuple(tuple(d.items()) for d in self.history_insurance_coverage),
            frozenset(self.address.items()),
            self.is_primary_holder,
            self.credit_score
        ))

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)


class Vehicle:
    def __init__(self,
                 registered_on: Applicant,
                 vehicle_use: str = "personal",
                 passed_safety_inspections: bool = False,
                 date_creation: date = None,
                 vehicle_type: str = "normal"):
        self.registered_on = registered_on
        self.vehicle_use = vehicle_use
        self.passed_safety_inspections = passed_safety_inspections
        self.date_creation = date_creation
        self.vehicle_type = vehicle_type

    def to_dict(self) -> dict:
        return {
            "registered_on": self.registered_on.to_dict(),
            "vehicle_use": self.vehicle_use,
            "passed_safety_inspections": self.passed_safety_inspections,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "vehicle_type": self.vehicle_type
        }

    @staticmethod
    def from_dict(data: dict):
        return Vehicle(
            registered_on=Applicant.from_dict(data["registered_on"]),
            vehicle_use=data.get("vehicle_use", "personal"),
            passed_safety_inspections=data.get("passed_safety_inspections", False),
            date_creation=date.fromisoformat(data["date_creation"]) if data.get("date_creation") else None,
            vehicle_type=data.get("vehicle_type", "normal")
        )

    def __eq__(self, other):
        if not isinstance(other, Vehicle):
            return False
        return (
                self.registered_on == other.registered_on and
                self.vehicle_use == other.vehicle_use and
                self.passed_safety_inspections == other.passed_safety_inspections and
                self.date_creation == other.date_creation and
                self.vehicle_type == other.vehicle_type
        )

    def __hash__(self):
        return hash((
            self.registered_on,
            self.vehicle_use,
            self.passed_safety_inspections,
            self.date_creation,
            self.vehicle_type
        ))

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)


class CarInsuranceRequest:
    def __init__(self, applicants: List[Applicant], vehicle: Vehicle, liability_coverage: float, state_min_liability: float):
        self.applicants = applicants
        self.vehicle = vehicle
        self.liability_coverage = liability_coverage
        self.state_min_liability = state_min_liability

    def primary_applicant(self) -> Applicant:
        return next((applicant for applicant in self.applicants if applicant.is_primary_holder), None)

    def to_dict(self) -> dict:
        return {
            "applicants": json.dumps(
                [applicant.to_dict() for applicant in self.applicants], indent=2  # Pretty print JSON
            ).replace("\n", ""),
            "vehicle": json.dumps(self.vehicle.to_dict()).replace("\n", ""),
            "liability_coverage": self.liability_coverage,
            "state_min_liability": self.state_min_liability
        }

    @staticmethod
    def from_dict(data: dict):
        return CarInsuranceRequest(
            applicants=[Applicant.from_dict(a) for a in json.loads(data["applicants"])],
            vehicle=Vehicle.from_dict(json.loads(data["vehicle"])),
            liability_coverage=float(data["liability_coverage"]),
            state_min_liability=float(data["state_min_liability"])
        )

    def __eq__(self, other):
        if not isinstance(other, CarInsuranceRequest):
            return False
        return (
                self.applicants == other.applicants and
                self.vehicle == other.vehicle and
                self.liability_coverage == other.liability_coverage and
                self.state_min_liability == other.state_min_liability
        )

    def __hash__(self):
        return hash((
            frozenset(self.applicants),
            self.vehicle,
            self.liability_coverage,
            self.state_min_liability
        ))

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)


class TestCarInsuranceRequest(unittest.TestCase):

    def setUp(self):
        """Set up common test data for CarInsuranceRequest."""
        self.license = DrivingLicense(
            status="valid",
            issue_date=date(2018, 5, 20),
            expiration_date=date(2028, 5, 20),
            issue_country="us"
        )
        self.applicants = [Applicant(
            birth_date=date(1990, 6, 15),
            driving_license=self.license,
            credit_score=750
        )]
        self.vehicle = Vehicle(
            registered_on=self.applicants[0],
            vehicle_use="personal",
            passed_safety_inspections=True,
            date_creation=date(2020, 1, 1),
            vehicle_type="normal"
        )
        self.car_insurance_request = CarInsuranceRequest(
            applicants=self.applicants,
            vehicle=self.vehicle,
            liability_coverage=100000,
            state_min_liability=50000
        )

    def test_initialization(self):
        """Test object initialization."""
        self.assertEqual(self.car_insurance_request.applicants, self.applicants)
        self.assertEqual(self.car_insurance_request.vehicle, self.vehicle)
        self.assertEqual(self.car_insurance_request.liability_coverage, 100000)
        self.assertEqual(self.car_insurance_request.state_min_liability, 50000)

    def test_equality(self):
        """Test equality operator (__eq__)."""
        another_request = CarInsuranceRequest(
            applicants=self.applicants,
            vehicle=self.vehicle,
            liability_coverage=100000,
            state_min_liability=50000
        )
        self.assertEqual(self.car_insurance_request, another_request)

    def test_hash(self):
        """Test hashing consistency."""
        self.assertEqual(hash(self.car_insurance_request), hash(self.car_insurance_request))

    def test_repr(self):
        """Test string representation (__repr__)."""
        repr_output = repr(self.car_insurance_request)
        self.assertIn('"liability_coverage": 100000', repr_output)
        self.assertIn('"state_min_liability": 50000', repr_output)


if __name__ == '__main__':
    unittest.main()

import csv
import json
import unittest

from luggage import Luggage


class LuggageComplianceRequest:
    def __init__(self, travel_class: str, age_category: str, luggages: list = None):
        """
        Represents a request to assess luggage compliance for a specific travel class and age category.

        Parameters:
        - travel_class (str): The travel class ("economy", "business", "first").
        - age_category (str): The age category of the passenger ("adult", "child", "infant").
        - luggages (list[Luggage]): A list of Luggage objects.
        """
        self.travel_class = travel_class  # "economy", "business", "first"
        self.age_category = age_category  # "adult", "child", "infant"
        self.luggages = luggages or []  # Default to an empty list

    def add_luggage(self, luggage: Luggage):
        """Adds a Luggage object to the request."""
        self.luggages.append(luggage)

    def to_dict(self) -> dict:
        """Converts the request into a dictionary with pretty JSON for CSV storage."""
        return {
            "travel_class": self.travel_class,
            "age_category": self.age_category,
            "luggages": json.dumps(
                [luggage.to_dict() for luggage in self.luggages], indent=2  # Pretty print JSON
            )
        }

    @staticmethod
    def from_dict(data: dict):
        """Creates a LuggageComplianceRequest object from a dictionary."""
        return LuggageComplianceRequest(
            travel_class=data["travel_class"],
            age_category=data["age_category"],
            luggages=[Luggage.from_dict(l) for l in json.loads(data["luggages"])]
        )

    @staticmethod
    def save_to_csv(filename: str, compliance_requests: list):
        """Saves a list of LuggageComplianceRequest objects to a CSV file, with one row per request."""
        if not compliance_requests:
            return

        fieldnames = ["travel_class", "age_category", "luggages"]

        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for request in compliance_requests:
                row = request.to_dict()
                row["luggages"] = json.dumps(json.loads(row["luggages"]), indent=2)  # Reformat JSON
                writer.writerow(row)

    @staticmethod
    def load_from_csv(filename: str) -> list:
        """Loads a list of LuggageComplianceRequest objects from a CSV file."""
        requests = []
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                row["luggages"] = json.loads(row["luggages"].replace("\n", ""))  # Remove line breaks for parsing
                requests.append(LuggageComplianceRequest.from_dict(row))
        return requests

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)  # Pretty print for better readability


class TestLuggageCompliance(unittest.TestCase):

    def setUp(self):
        """Initialize for all tests."""

    def test_1(self):
        bag1 = Luggage(storage="carry-on", weight=7.0, excess=False,
                       dim={"height": 55.0, "width": 40.0, "depth": 23.0, "unit": "cm"})
        bag2 = Luggage(storage="checked", weight=25.0, excess=True,
                       dim={"height": 70.0, "width": 50.0, "depth": 30.0, "unit": "cm"})

        request1 = LuggageComplianceRequest(travel_class="business", age_category="adult", luggages=[bag1, bag2])
        request2 = LuggageComplianceRequest(travel_class="economy", age_category="child", luggages=[bag1])

        requests = [request1, request2]

        self.assertEqual(len(requests), 2)

        print(request1)


if __name__ == "__main__":
    unittest.main()
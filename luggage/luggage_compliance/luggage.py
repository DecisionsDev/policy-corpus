import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import csv
import unittest

class Luggage:
    def __init__(
        self,
        storage: str = "carry-on",  # "carry-on", "checked", "special"
        excess: bool = False,
        special: bool = False,
        compliance: bool = False,
        weight: float = 0.0,  # in kg
        dim: dict = None  # Dimensions stored in a nested dict
    ):
        self.storage = storage
        self.excess = excess
        self.special = special
        self.compliance = compliance
        self.weight = weight
        self.dim = dim or {
            "height": 0.0,
            "width": 0.0,
            "depth": 0.0,
            "unit": "cm"
        }

    def get_volume(self) -> float:
        """Calculates the volume of the luggage in cubic centimeters."""
        return self.dim["height"] * self.dim["width"] * self.dim["depth"]

    def is_oversized(self, max_dim: float) -> bool:
        """Checks if any dimension exceeds the allowed max_dim (cm)."""
        return max(self.dim["height"], self.dim["width"], self.dim["depth"]) > max_dim

    def to_dict(self) -> dict:
        """Converts the luggage object into a dictionary matching the JSON structure."""
        return {
            "storage": self.storage,
            "excess": self.excess,
            "special": self.special,
            "compliance": self.compliance,
            "weight": self.weight,
            "height": self.dim["height"],
            "width": self.dim["width"],
            "depth": self.dim["depth"],
            "unit": self.dim["unit"]
        }

    @staticmethod
    def from_dict(data: dict):
        """Creates a Luggage object from a dictionary."""
        return Luggage(
            storage=data["storage"],
            excess=data.get("excess", False),
            special=data.get("special", False),
            compliance=data.get("compliance", False),
            weight=data["weight"],
            dim={
                "height": data["height"],
                "width": data["width"],
                "depth": data["depth"],
                "unit": data["unit"]
            }
        )

    @staticmethod
    def save_to_csv(filename: str, luggage_list: list):
        """Saves a list of Luggage objects to a CSV file."""
        if not luggage_list:
            return

        fieldnames = ["storage", "excess", "special", "compliance", "weight", "height", "width", "depth", "unit"]

        with open(filename, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for luggage in luggage_list:
                writer.writerow(luggage.to_dict())

    @staticmethod
    def load_from_csv(filename: str) -> list:
        """Loads Luggage objects from a CSV file."""
        luggage_list = []
        with open(filename, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                row["excess"] = row["excess"].lower() == "true"
                row["special"] = row["special"].lower() == "true"
                row["compliance"] = row["compliance"].lower() == "true"
                row["weight"] = float(row["weight"])
                row["height"] = float(row["height"])
                row["width"] = float(row["width"])
                row["depth"] = float(row["depth"])
                luggage_list.append(Luggage.from_dict(row))
        return luggage_list

    def __eq__(self, other):
        if not isinstance(other, Luggage):
            return False
        return (
                self.storage == other.storage and
                self.weight == other.weight and
                self.dim == other.dim and
                self.excess == other.excess and
                self.special == other.special and
                self.compliance == other.compliance
        )

    def __hash__(self):
        """Defines a hash so Luggage objects can be stored in sets/dictionaries."""
        return hash((
            self.storage,
            self.weight,
            frozenset(self.dim.items()),  # Convert dict to frozenset for hashing
            self.excess,
            self.special,
            self.compliance
        ))

    def __repr__(self):
        return (
            f"Luggage(storage={self.storage}, weight={self.weight}kg, "
            f"dim={self.dim}, excess={self.excess}, special={self.special}, "
            f"compliance={self.compliance})"
        )

class TestLuggageCompliance(unittest.TestCase):

    def setUp(self):
        """Initialize for all tests."""


    def test_carry_on_exceeds_quantity(self):
        bag1 = Luggage(
            storage="carry-on",
            excess=False,
            special=False,
            compliance=True,
            weight=7.0,
            dim={"height": 55.0, "width": 40.0, "depth": 23.0, "unit": "cm"}
        )

        bag2 = Luggage(
            storage="checked",
            excess=True,
            special=False,
            compliance=False,
            weight=25.0,
            dim={"height": 70.0, "width": 50.0, "depth": 30.0, "unit": "cm"}
        )

        luggage_list = [bag1, bag2]

        self.assertEqual(len(luggage_list), 2)


if __name__ == "__main__":
    unittest.main()
import random
import json
from typing import List, Dict
import pandas as pd

from common.common.DataGenerator import DataGenerator
from luggage_compliance import LuggageCompliance
from luggage import Luggage
from luggage_compliance_request import LuggageComplianceRequest

class LuggageDataGenerator(DataGenerator):
    COLUMN_NAMES = [
        "travel_class", "age_category", "luggages", "eligibility",
        "compliance_result", "compliance_message", "cargo_items", "fees"
    ]

    # Constants for luggage generation
    TRAVEL_CLASSES = ["Economy", "Business", "First"]
    AGE_CATEGORIES = ["adult", "child", "infant"]
    STORAGE_TYPES = ["carry-on", "checked", "personal"]
    MAX_DIMENSIONS = {"height": 100, "width": 80, "depth": 50}
    MAX_WEIGHT = 50

    def __init__(self):
        self.compliance_checker = LuggageCompliance()

    def generate_test_dataset(self, num_samples=100) -> pd.DataFrame:
        data = []
        eligible_count = 0

        for _ in range(num_samples):
            travel_class = random.choice(self.TRAVEL_CLASSES)
            age_category = random.choice(self.AGE_CATEGORIES)
            luggages = self.generate_luggages()
            request = LuggageComplianceRequest(travel_class, age_category, luggages)

            compliance_result, compliance_message, cargo_items, fees = self.compliance_checker.test_eligibility(request)
            eligibility = compliance_result and not cargo_items

            if eligibility:
                eligible_count += 1

            data.append({
                "travel_class": travel_class,
                "age_category": age_category,
                "luggages": json.dumps([luggage.to_dict() for luggage in luggages]),
                "eligibility": eligibility,
                "compliance_result": compliance_result,
                "compliance_message": compliance_message,
                "cargo_items": json.dumps([item.to_dict() for item in cargo_items]) if cargo_items else None,
                "fees": fees
            })

            # Ensure at least 50% of the cases are eligible
            if _ == num_samples // 2 and eligible_count < num_samples // 2:
                data = self.adjust_eligibility(data, num_samples // 2 - eligible_count)

        return pd.DataFrame(data)

    def adjust_eligibility(self, data, needed_eligible):
        for _ in range(needed_eligible):
            travel_class = random.choice(self.TRAVEL_CLASSES)
            age_category = random.choice(self.AGE_CATEGORIES)
            luggages = self.generate_eligible_luggages(travel_class, age_category)
            request = LuggageComplianceRequest(travel_class, age_category, luggages)

            compliance_result, compliance_message, cargo_items, fees = self.compliance_checker.test_eligibility(request)

            data.append({
                "travel_class": travel_class,
                "age_category": age_category,
                "luggages": json.dumps([luggage.to_dict() for luggage in luggages]),
                "eligibility": True,
                "compliance_result": compliance_result,
                "compliance_message": compliance_message,
                "cargo_items": None,
                "fees": fees
            })
        return data

    def generate_luggages(self) -> List[Luggage]:
        num_luggages = random.randint(1, 5)
        luggages = []
        for _ in range(num_luggages):
            storage = random.choice(self.STORAGE_TYPES)
            excess = random.choice([True, False])
            special = random.choice([True, False])
            compliance = random.choice([True, False])
            weight = round(random.uniform(0, self.MAX_WEIGHT), 2)
            dim = {
                "height": round(random.uniform(0, self.MAX_DIMENSIONS["height"]), 2),
                "width": round(random.uniform(0, self.MAX_DIMENSIONS["width"]), 2),
                "depth": round(random.uniform(0, self.MAX_DIMENSIONS["depth"]), 2),
                "unit": "cm"
            }
            luggage = Luggage(storage, excess, special, compliance, weight, dim)
            luggages.append(luggage)
        return luggages

    def generate_eligible_luggages(self, travel_class, age_category) -> List[Luggage]:
        while True:
            luggages = []
            class_policy = self.compliance_checker.classes[travel_class]

            # Generate carry-on luggage
            for _ in range(class_policy["carry_on"]["quantity"]):
                storage = "carry-on"
                excess = False
                special = False
                compliance = True
                weight = round(random.uniform(0, class_policy["carry_on"]["weight_limit"]), 2)
                dim = {
                    "height": round(random.uniform(0, class_policy["carry_on"]["size_limit"][0]), 2),
                    "width": round(random.uniform(0, class_policy["carry_on"]["size_limit"][1]), 2),
                    "depth": round(random.uniform(0, class_policy["carry_on"]["size_limit"][2]), 2),
                    "unit": "cm"
                }
                luggage = Luggage(storage, excess, special, compliance, weight, dim)
                luggages.append(luggage)

            # Generate checked luggage
            for _ in range(class_policy["checked"]["allowance"]):
                storage = "checked"
                excess = False
                special = False
                compliance = True
                weight = round(random.uniform(0, class_policy["checked"]["weight_limit"]), 2)
                dim = {
                    "height": round(random.uniform(0, class_policy["checked"]["size_limit"]), 2),
                    "width": round(random.uniform(0, class_policy["checked"]["size_limit"]), 2),
                    "depth": round(random.uniform(0, class_policy["checked"]["size_limit"]), 2),
                    "unit": "cm"
                }
                luggage = Luggage(storage, excess, special, compliance, weight, dim)
                luggages.append(luggage)

            request = LuggageComplianceRequest(travel_class, age_category, luggages)
            compliance_result, _, _, _ = self.compliance_checker.test_eligibility(request)

            if compliance_result:
                return luggages

    def determine_eligibility(self, row) -> bool:
        return row["eligibility"]

    def get_constant(self) -> Dict:
        return super().get_constant()

def format_data_units(n):
    nb_units = round(n / 1000000)
    if nb_units >= 1:
        unit = "M"
    else:
        nb_units = round(n / 1000)
        if nb_units >= 1:
            unit = "K"
        else:
            nb_units = n
            unit = ""

    label = f'{nb_units}{unit}'
    return label

if __name__ == "__main__":
    sizes = [100, 1000]
             # 10000, 100000]

    generator = LuggageDataGenerator()

    for size in sizes:
        df = generator.generate_test_dataset(size)

        data_units = format_data_units(size)
        df.to_csv(f'luggage_policy_test_dataset_{data_units}.csv', index=False)

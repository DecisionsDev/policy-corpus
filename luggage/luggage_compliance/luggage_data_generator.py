import random
import json
import sys
import os
from typing import List, Dict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_data_generator import DataGenerator, format_data_units
from luggage_compliance import LuggageCompliance
from luggage import Luggage
from luggage_compliance_request import LuggageComplianceRequest


class LuggageDataGenerator(DataGenerator):
    COLUMN_NAMES = [
        "travel_class", "age_category", "luggages", "eligibility",
        "compliance_result", "compliance_message", "cargo_items", "fees"
    ]

    EVAL_COLUMN_NAMES = ["eligibility", "compliance_result", "fees", "compliance_message", "cargo_items"]

    TRAVEL_CLASSES = ["Economy", "Business", "First"]
    AGE_CATEGORIES = ["adult", "child", "infant"]
    STORAGE_TYPES = ["carry-on", "checked", "personal"]
    MAX_DIMENSIONS = {"height": 100, "width": 80, "depth": 50}
    MAX_WEIGHT = 50

    def __init__(self):
        super().__init__(LuggageCompliance())

    def generate_eligible_case(self) -> Dict:
        travel_class = random.choice(self.TRAVEL_CLASSES)
        age_category = random.choice(self.AGE_CATEGORIES)
        luggages = self.generate_eligible_luggages(travel_class, age_category)
        request = LuggageComplianceRequest(travel_class, age_category, luggages)
        compliance_result,  compliance_message, carry_on_to_check, cargo_items, fees = self.policy_checker.test_eligibility(request)

        return {
            "travel_class": travel_class,
            "age_category": age_category,
            "luggages": json.dumps([luggage.to_dict() for luggage in luggages]),
            "eligibility": True,
            "compliance_result": compliance_result,
            "compliance_message": compliance_message,
            "moved_to_checked": json.dumps([item.to_dict() for item in carry_on_to_check]) if carry_on_to_check else None,
            "cargo_items": None,
            "fees": fees
        }

    def generate_non_eligible_case(self) -> Dict:
        travel_class = random.choice(self.TRAVEL_CLASSES)
        age_category = random.choice(self.AGE_CATEGORIES)
        luggages = self.generate_luggages()
        request = LuggageComplianceRequest(travel_class, age_category, luggages)
        compliance_result, compliance_message, carry_on_to_check, cargo_items, fees = self.policy_checker.test_eligibility(request)
        eligibility = compliance_result and not cargo_items

        return {
            "travel_class": travel_class,
            "age_category": age_category,
            "luggages": json.dumps([luggage.to_dict() for luggage in luggages]),
            "eligibility": eligibility,
            "compliance_result": compliance_result,
            "compliance_message": compliance_message,
            "moved_to_checked":  json.dumps([item.to_dict() for item in carry_on_to_check]) if carry_on_to_check else None,
            "cargo_items": json.dumps([item.to_dict() for item in cargo_items]) if cargo_items else None,
            "fees": fees
        }

    def generate_luggages(self) -> List[Luggage]:
        num_luggages = random.randint(1, 5)
        return [
            Luggage(
                storage=random.choice(self.STORAGE_TYPES),
                excess=random.choice([True, False]),
                special=random.choice([True, False]),
                compliance=random.choice([True, False]),
                weight=round(random.uniform(0, self.MAX_WEIGHT), 2),
                dim={
                    "height": round(random.uniform(0, self.MAX_DIMENSIONS["height"]), 2),
                    "width": round(random.uniform(0, self.MAX_DIMENSIONS["width"]), 2),
                    "depth": round(random.uniform(0, self.MAX_DIMENSIONS["depth"]), 2),
                    "unit": "cm"
                }
            )
            for _ in range(num_luggages)
        ]

    def generate_eligible_luggages(self, travel_class, age_category) -> List[Luggage]:
        while True:
            luggages = []
            class_policy = self.policy_checker.classes[travel_class]

            for _ in range(class_policy["carry_on"]["quantity"]):
                luggages.append(Luggage("carry-on", False, False, True,
                                        round(random.uniform(0, class_policy["carry_on"]["weight_limit"]), 2),
                                        {
                                            "height": round(
                                                random.uniform(0, class_policy["carry_on"]["size_limit"][0]), 2),
                                            "width": round(random.uniform(0, class_policy["carry_on"]["size_limit"][1]),
                                                           2),
                                            "depth": round(random.uniform(0, class_policy["carry_on"]["size_limit"][2]),
                                                           2),
                                            "unit": "cm"
                                        }))

            for _ in range(class_policy["checked"]["allowance"]):
                luggages.append(Luggage("checked", False, False, True,
                                        round(random.uniform(0, class_policy["checked"]["weight_limit"]), 2),
                                        {
                                            "height": round(random.uniform(0, class_policy["checked"]["size_limit"]),
                                                            2),
                                            "width": round(random.uniform(0, class_policy["checked"]["size_limit"]), 2),
                                            "depth": round(random.uniform(0, class_policy["checked"]["size_limit"]), 2),
                                            "unit": "cm"
                                        }))

            request = LuggageComplianceRequest(travel_class, age_category, luggages)
            compliance_result, _, _, _, _ = self.policy_checker.test_eligibility(request)

            if compliance_result:
                return luggages


if __name__ == "__main__":
    sizes = [100, 1000]
    generator = LuggageDataGenerator()

    for size in sizes:
        df = generator.generate_test_dataset(size)
        data_units = format_data_units(size)
        df.to_csv(f'luggage_policy_test_dataset_{data_units}.csv', index=False)

import random
import pandas as pd

from common.DataGenerator import DataGenerator


class LuggageDataGenerator(DataGenerator):
    COLUMN_NAMES = [
        'travel_class',
        'passenger_type',
        'carry_on_weight',
        'num_carry_on_items',
        'num_personal_items',
        'carry_on_items',
        'personal_items',
        'checked_items',
        'num_checked_items',
        'eligibility'
    ]

    CLASS_LIMITS = {
        "Economy": {"carry_on_weight": 7, "carry_on_size": [55, 40, 23], "weight_limit": 23, "size_limit": 158},
        "Business": {"carry_on_weight": 12, "carry_on_size": [55, 40, 23], "weight_limit": 32, "size_limit": 158},
        "First": {"carry_on_weight": 12, "carry_on_size": [55, 40, 23], "weight_limit": 32, "size_limit": 158}
    }

    INFANT_LIMITS = {"weight_limit": 10, "size_limit": 158}

    CLASSES = ["Economy", "Business", "First"]
    PASSENGER_TYPES = ["adult", "child", "infant"]

    def generate_random_dimensions(self, max_length, max_width, max_height):
        return [
            random.randint(1, max_length),
            random.randint(1, max_width),
            random.randint(1, max_height)
        ]

    def enforce_carry_on_policy(self, travel_class, carry_on_items, personal_items):
        limits = self.CLASS_LIMITS[travel_class]
        valid_carry_on_items = []
        valid_personal_items = []
        total_weight = 0

        for item in carry_on_items:
            if all(d <= s for d, s in zip(item["dimensions"], limits["carry_on_size"])) and total_weight + item["weight"] <= limits["carry_on_weight"]:
                valid_carry_on_items.append(item)
                total_weight += item["weight"]

        for item in personal_items:
            if all(d <= s for d, s in zip(item["dimensions"], limits["carry_on_size"])) and total_weight + item["weight"] <= limits["carry_on_weight"]:
                valid_personal_items.append(item)
                total_weight += item["weight"]

        return valid_carry_on_items, valid_personal_items, round(total_weight, 2)

    def enforce_checked_policy(self, travel_class, passenger_type, checked_items):
        limits = self.INFANT_LIMITS if passenger_type == "infant" else self.CLASS_LIMITS[travel_class]
        valid_checked_items = []

        for item in checked_items:
            total_size = sum(item["dimensions"])
            if item["weight"] <= limits["weight_limit"] and total_size <= limits["size_limit"]:
                valid_checked_items.append(item)

        return valid_checked_items

    def determine_eligibility(self, row):
        # Example eligibility criteria
        return row['eligibility'] == "True"

    def generate_test_dataset(self, num_samples=100):
        dataset = []
        for i in range(num_samples):
            travel_class = random.choice(self.CLASSES)
            passenger_type = random.choice(self.PASSENGER_TYPES)

            carry_on_items = [
                {
                    "weight": round(random.uniform(0.5, 5.0), 2),
                    "dimensions": self.generate_random_dimensions(55, 40, 23)
                } for _ in range(random.randint(0, 3))
            ]
            personal_items = [
                {
                    "weight": round(random.uniform(0.5, 3.0), 2),
                    "dimensions": self.generate_random_dimensions(40, 30, 20)
                } for _ in range(random.randint(0, 1))
            ]

            carry_on_weight = sum(item["weight"] for item in carry_on_items + personal_items)

            # Ensure checked_items is always initialized
            checked_items = []

            if i < num_samples * 0.1:  # Generate non-eligible records (10%)
                # Exceed weight or size limits randomly
                if random.choice([True, False]):
                    carry_on_items.append({"weight": round(random.uniform(8.0, 15.0), 2), "dimensions": [60, 45, 30]})
                    carry_on_weight += carry_on_items[-1]["weight"]
                else:
                    checked_items.append(
                        {"weight": round(random.uniform(33.0, 40.0), 2), "dimensions": [100, 80, 70]}  # Oversized and overweight
                    )
                personal_items.append({"weight": round(random.uniform(3.5, 5.0), 2), "dimensions": [50, 35, 25]})
                carry_on_weight += personal_items[-1]["weight"]
                eligibility = "False"
            else:
                carry_on_items, personal_items, carry_on_weight = self.enforce_carry_on_policy(travel_class, carry_on_items, personal_items)

                checked_items = [
                    {
                        "weight": round(random.uniform(5.0, 35.0), 2),
                        "dimensions": self.generate_random_dimensions(80, 70, 60)
                    } for _ in range(random.randint(0, 5))
                ]

                checked_items = self.enforce_checked_policy(travel_class, passenger_type, checked_items)
                eligibility = "True"

            for item in carry_on_items:
                item["dimensions"] = "x".join(str(d) for d in item["dimensions"])
            for item in personal_items:
                item["dimensions"] = "x".join(str(d) for d in item["dimensions"])
            for item in checked_items:
                item["dimensions"] = "x".join(str(d) for d in item["dimensions"])

            dataset.append({
                "travel_class": travel_class,
                "passenger_type": passenger_type,
                "carry_on_weight": round(carry_on_weight, 2),
                "num_carry_on_items": len(carry_on_items),
                "num_personal_items": len(personal_items),
                "carry_on_items": " | ".join(f"{item['weight']}kg ({item['dimensions']})" for item in carry_on_items),
                "personal_items": " | ".join(f"{item['weight']}kg ({item['dimensions']})" for item in personal_items),
                "checked_items": " | ".join(f"{item['weight']}kg ({item['dimensions']})" for item in checked_items),
                "num_checked_items": len(checked_items),
                "eligibility": eligibility
            })

        return pd.DataFrame(dataset)


# Generate the dataset
generator = LuggageDataGenerator()
dataset = generator.generate_test_dataset(num_samples=100)

# Save to CSV
dataset.to_csv('luggage_policy_test_dataset.csv', index=False)
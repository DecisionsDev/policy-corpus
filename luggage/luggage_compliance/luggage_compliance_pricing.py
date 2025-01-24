from common.Policy import Policy


class LuggagePolicy(Policy):
    def __init__(self):
        self.classes = {
            "Economy": {
                "carry_on": {"quantity": 1, "weight_limit": 7, "size_limit": [55, 40, 23]},
                "checked": {"allowance": 1, "weight_limit": 23, "size_limit": 158}
            },
            "Business": {
                "carry_on": {"quantity": 2, "weight_limit": 12, "size_limit": [55, 40, 23]},
                "checked": {"allowance": 2, "weight_limit": 32, "size_limit": 158}
            },
            "First": {
                "carry_on": {"quantity": 2, "weight_limit": 12, "size_limit": [55, 40, 23]},
                "checked": {"allowance": 3, "weight_limit": 32, "size_limit": 158}
            }
        }
        self.child_allowances = {
            "child": {"checked": {"allowance": 1, "weight_limit": 23, "size_limit": 158}},
            "infant": {"checked": {"allowance": 1, "weight_limit": 10, "size_limit": 158}, "additional": "collapsible stroller"}
        }
        self.excess_fees = {
            "overweight": 75,
            "oversize": 100,
            "extra_piece": 150
        }

    def validate_carry_on(self, travel_class, carry_on_items, personal_items, total_weight):
        class_policy = self.classes[travel_class]["carry_on"]
        if len(carry_on_items) + len(personal_items) > class_policy["quantity"] + 1:
            return False, "Exceeded carry-on quantity allowance (including personal items)."
        if total_weight > class_policy["weight_limit"]:
            return False, "Exceeded carry-on weight limit."
        for item in carry_on_items:
            if any(dim > lim for dim, lim in zip(item, class_policy["size_limit"])):
                return False, "Carry-on bag exceeds size limits."
        return True, "Carry-on luggage complies with the policy."

    def validate_checked_baggage(self, travel_class, checked_items, passenger_type="adult"):
        class_policy = self.classes[travel_class]["checked"]
        fees = 0

        if passenger_type in self.child_allowances:
            class_policy = self.child_allowances[passenger_type]["checked"]

        if len(checked_items) > class_policy["allowance"]:
            fees += self.excess_fees["extra_piece"] * (len(checked_items) - class_policy["allowance"])

        for item in checked_items:
            weight, dimensions = item["weight"], item["dimensions"]
            total_size = sum(dimensions)

            if weight > class_policy["weight_limit"]:
                fees += self.excess_fees["overweight"]
            if total_size > class_policy["size_limit"] and total_size <= 203:
                fees += self.excess_fees["oversize"]
            if weight > 32 or total_size > 203:
                return False, f"Item with weight {weight}kg or size {total_size}cm must be shipped as cargo.", fees

        return True, f"Checked luggage complies with the policy. Fees: ${fees}", fees

    def validate_luggage(self, travel_class, carry_on_items, personal_items, carry_on_weight, checked_items, passenger_type="adult"):
        carry_on_result, carry_on_message = self.validate_carry_on(travel_class, carry_on_items, personal_items, carry_on_weight)
        if not carry_on_result:
            return carry_on_message

        checked_result, checked_message, fees = self.validate_checked_baggage(travel_class, checked_items, passenger_type)
        if not checked_result:
            return checked_message

        return f"Luggage complies with the policy. Total fees: ${fees}"

    def test_eligibility(self, info):
        travel_class = info['travel_class']
        passenger_type = info['passenger_type']
        carry_on_weight = info['carry_on_weight']
        num_carry_on_items = info['num_carry_on_items']
        num_personal_items = info['num_personal_items']
        carry_on_items = info['carry_on_items']
        personal_items = info['personal_items']
        checked_items = info['checked_items']
        num_checked_items = info['num_checked_items']

        # Ensure the number of items matches the provided items
        if num_carry_on_items != len(carry_on_items):
            return False, "Mismatch between number of carry-on items and provided carry-on items."
        if num_personal_items != len(personal_items):
            return False, "Mismatch between number of personal items and provided personal items."
        if num_checked_items != len(checked_items):
            return False, "Mismatch between number of checked items and provided checked items."

        # Validate luggage
        result_message = self.validate_luggage(travel_class, carry_on_items, personal_items, carry_on_weight, checked_items, passenger_type)

        # Determine eligibility based on the result message
        if "complies with the policy" in result_message:
            return True, result_message
        else:
            return False, result_message

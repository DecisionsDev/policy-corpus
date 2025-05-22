import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.abstract_policy import Policy
from luggage import Luggage
from luggage_compliance_request import LuggageComplianceRequest

import unittest


class LuggageCompliance(Policy):
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
            "infant": {"checked": {"allowance": 1, "weight_limit": 10, "size_limit": 158},
                       "additional": "collapsible stroller"}
        }
        self.excess_fees = {
            "overweight": 75,
            "oversize": 100,
            "extra_piece": 150
        }

    def validate_carry_on(self, travel_class, carry_on_items, personal_items):
        class_policy = self.classes[travel_class]["carry_on"]
        checked_candidates = []

        total_items = carry_on_items + personal_items
        compliant_items = []
        for item in total_items:
            size_ok = all(dim <= lim for dim, lim in zip(
                [item.dim[k] for k in ["height", "width", "depth"]],
                class_policy["size_limit"]
            ))
            if not size_ok or item.weight > class_policy["weight_limit"]:
                checked_candidates.append(item)
            else:
                compliant_items.append(item)

        # Check quantity compliance
        max_items = class_policy["quantity"] + 1  # +1 for personal item
        if len(compliant_items) > max_items:
            # Move largest item(s) to checked baggage
            compliant_items.sort(key=lambda x: x.weight, reverse=True)
            overflow = compliant_items[max_items:]
            checked_candidates.extend(overflow)
            compliant_items = compliant_items[:max_items]

        if len(checked_candidates) > 0:
            return True, f"But {len(checked_candidates)} needs to be moved in checked luggages", checked_candidates

        return True, "Carry-on checked for compliance.", checked_candidates

    def validate_checked_baggage(self, travel_class, checked_items, passenger_type="adult", carry_on_capacity=0):
        class_policy = self.classes[travel_class]["checked"].copy()
        fees = 0
        cargo_items = []
        retained_checked_items = []
        message = ""

        if passenger_type in self.child_allowances:
            child_policy = self.child_allowances[passenger_type]["checked"]
            class_policy["allowance"] += child_policy["allowance"]
            class_policy["weight_limit"] = max(class_policy["weight_limit"], child_policy["weight_limit"])

        # Try to pull light checked items back into carry-on if there's room
        checked_items.sort(key=lambda x: x.weight)  # Try lightest first
        carryon_candidates = []
        for item in checked_items:
            dims = [item.dim[k] for k in ["height", "width", "depth"]]
            if (carry_on_capacity > 0 and
                    all(dim <= self.classes[travel_class]["carry_on"]["size_limit"][i] for i, dim in
                        enumerate(dims)) and
                    item.weight <= self.classes[travel_class]["carry_on"]["weight_limit"]):
                carryon_candidates.append(item)
                carry_on_capacity -= 1
            else:
                retained_checked_items.append(item)

        for item in retained_checked_items:
            weight = item.weight
            dimensions = [item.dim[k] for k in ["height", "width", "depth"]]
            total_size = sum(dimensions)

            if weight > 32 or total_size > 203:
                cargo_items.append(item)

            if weight > class_policy["weight_limit"]:
                fees += self.excess_fees["overweight"]
                message += f"The item with dimensions: {dimensions} and weight: {weight} is above weight limit; "

            if total_size > class_policy["size_limit"] and total_size <= 203:
                fees += self.excess_fees["oversize"]
                message += f"The item with dimensions: {dimensions} and total_size: {total_size} is above size limit; "

        excess_items = max(0, len(retained_checked_items) - class_policy["allowance"])
        fees += self.excess_fees["extra_piece"] * excess_items

        if excess_items > 0:
            message += f"There are {excess_items} excess_items: {retained_checked_items}; "

        if cargo_items:
            return False, "REASON OF FAILURE: Some items must be shipped as cargo due to weight or size. " + message, cargo_items, fees

        return True, message, cargo_items, fees

    def test_eligibility(self, request):
        carry_on_items = [x for x in request.luggages if x.storage == "carry-on"]
        personal_items = [x for x in request.luggages if x.storage == "personal"]
        checked_items = [x for x in request.luggages if x.storage == "checked"]

        # Validate carry-on and get moved items
        _, _, carry_on_to_check = self.validate_carry_on(request.travel_class, carry_on_items, personal_items)

        # Combine with original checked items
        all_checked_items = checked_items + carry_on_to_check

        # Carry-on space left after adjustment
        class_policy = self.classes[request.travel_class]["carry_on"]
        carry_on_capacity = class_policy["quantity"] + 1 - (
                    len(carry_on_items) + len(personal_items) - len(carry_on_to_check))

        # Validate checked baggage (including shifted ones)
        checked_result, checked_message, cargo_items, fees = self.validate_checked_baggage(
            request.travel_class, all_checked_items, request.age_category, carry_on_capacity
        )

        return checked_result, checked_message, carry_on_to_check, cargo_items, fees


def test1():
    # Instantiate the policy
    policy = LuggageCompliance()
    travel_class = "Economy"

    # Test case: Validate carry-on and checked luggage for Economy class
    bag1 = Luggage(storage="carry-on", weight=5.0, dim={"height": 50.0, "width": 40.0, "depth": 23.0, "unit": "cm"})
    bag2 = Luggage(storage="checked", weight=25.0, dim={"height": 40.0, "width": 30.0, "depth": 30.0, "unit": "cm"})
    bag3 = Luggage(storage="personal", weight=4.0, dim={"height": 20.0, "width": 50.0, "depth": 30.0, "unit": "cm"})
    compliance_request = LuggageComplianceRequest(travel_class="Business", age_category="adult",
                                                  luggages=[bag1, bag2, bag3])

    result = policy.test_eligibility(compliance_request)
    print(result)


class TestLuggageCompliance(unittest.TestCase):

    def setUp(self):
        self.policy = LuggageCompliance()

    def test_carry_on_exceeds_quantity(self):
        """Carry-on and personal items exceed quantity limit."""
        bag1 = Luggage(storage="carry-on", weight=5.0, dim={"height": 55, "width": 40, "depth": 20, "unit": "cm"})
        bag2 = Luggage(storage="carry-on", weight=5.0, dim={"height": 55, "width": 40, "depth": 23, "unit": "cm"})
        bag3 = Luggage(storage="personal", weight=2.0, dim={"height": 30, "width": 20, "depth": 10, "unit": "cm"})
        bag4 = Luggage(storage="personal", weight=2.0, dim={"height": 30, "width": 20, "depth": 10, "unit": "cm"})
        compliance_request = LuggageComplianceRequest("Economy", "adult", [bag1, bag2, bag3, bag4])

        result = self.policy.test_eligibility(compliance_request)
        self.assertFalse(result[0])
        self.assertIn("Exceeded carry-on quantity allowance", result[1])

    def test_carry_on_exceeds_weight(self):
        """Combined carry-on weight exceeds the limit."""
        bag1 = Luggage(storage="carry-on", weight=8.0, dim={"height": 55, "width": 40, "depth": 20, "unit": "cm"})
        bag2 = Luggage(storage="personal", weight=3.0, dim={"height": 30, "width": 20, "depth": 10, "unit": "cm"})
        compliance_request = LuggageComplianceRequest("Economy", "adult", [bag1, bag2])

        result = self.policy.test_eligibility(compliance_request)
        self.assertFalse(result[0])
        self.assertIn("Exceeded carry-on weight limit", result[1])

    def test_carry_on_exceeds_size(self):
        """Carry-on bag exceeds size limits."""
        bag1 = Luggage(storage="carry-on", weight=5.0, dim={"height": 60, "width": 45, "depth": 30, "unit": "cm"})
        compliance_request = LuggageComplianceRequest("Economy", "adult", [bag1])

        result = self.policy.test_eligibility(compliance_request)
        self.assertFalse(result[0])
        self.assertIn("Carry-on bag exceeds size limits", result[1])

    def test_checked_baggage_exceeds_allowance(self):
        """Checked baggage exceeds allowance."""
        bag1 = Luggage(storage="checked", weight=20.0, dim={"height": 70, "width": 50, "depth": 30, "unit": "cm"})
        bag2 = Luggage(storage="checked", weight=20.0, dim={"height": 70, "width": 50, "depth": 30, "unit": "cm"})
        bag3 = Luggage(storage="checked", weight=20.0, dim={"height": 70, "width": 50, "depth": 30, "unit": "cm"})
        compliance_request = LuggageComplianceRequest("Economy", "adult", [bag1, bag2, bag3])

        result = self.policy.test_eligibility(compliance_request)
        self.assertTrue(result[0])  # Valid but with fees
        self.assertGreater(result[3], 0)

    def test_checked_baggage_exceeds_allowance(self):
        """Checked baggage exceeds allowance."""
        bag1 = Luggage(storage="checked", weight=20.0, dim={"height": 70, "width": 50, "depth": 30, "unit": "cm"})
        bag2 = Luggage(storage="checked", weight=20.0, dim={"height": 70, "width": 50, "depth": 30, "unit": "cm"})
        bag3 = Luggage(storage="checked", weight=20.0, dim={"height": 70, "width": 50, "depth": 30, "unit": "cm"})
        compliance_request = LuggageComplianceRequest("Economy", "adult", [bag1, bag2, bag3])

        result = self.policy.test_eligibility(compliance_request)
        self.assertTrue(result[0])  # Valid but with fees
        self.assertGreater(result[3], 0)

    def test_checked_baggage_overweight(self):
        """Checked baggage is overweight."""
        bag1 = Luggage(storage="checked", weight=33.0, dim={"height": 70, "width": 50, "depth": 30, "unit": "cm"})
        compliance_request = LuggageComplianceRequest("Economy", "adult", [bag1])

        result = self.policy.test_eligibility(compliance_request)
        self.assertFalse(result[0])
        self.assertIn("Some items must be shipped as cargo due to weight or size.", result[1])

    def test_checked_baggage_oversized(self):
        """Checked baggage is oversized but within limits."""
        bag1 = Luggage(storage="checked", weight=25.0, dim={"height": 100, "width": 60, "depth": 50, "unit": "cm"})
        compliance_request = LuggageComplianceRequest("Economy", "adult", [bag1])

        result = self.policy.test_eligibility(compliance_request)
        self.assertFalse(result[0])
        self.assertGreater(result[3], 0)

    def test_checked_baggage_max_exceeded(self):
        """Checked baggage is too large or too heavy."""
        bag1 = Luggage(storage="checked", weight=35.0, dim={"height": 100, "width": 80, "depth": 50, "unit": "cm"})
        compliance_request = LuggageComplianceRequest("Economy", "adult", [bag1])

        result = self.policy.test_eligibility(compliance_request)
        self.assertFalse(result[0])
        self.assertIn("Some items must be shipped as cargo due to weight or size.", result[1])
        self.assertGreater(result[3], 0)


if __name__ == "__main__":
    unittest.main()

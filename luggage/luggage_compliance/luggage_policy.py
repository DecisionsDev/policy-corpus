import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_policy import Policy
from luggage import Luggage
from luggage_compliance_request import LuggageComplianceRequest

import unittest


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

        # Compute total weight of carry-on and personal items
        total_weight = sum(item.weight for item in carry_on_items + personal_items)

        # Check quantity
        if len(carry_on_items) + len(personal_items) > class_policy["quantity"] + 1:
            return False, "Exceeded carry-on quantity allowance (including personal items)."

        # Check weight
        if total_weight > class_policy["weight_limit"]:
            return False, "Exceeded carry-on weight limit."

        # Check size
        for item in carry_on_items:
            # if any(dim > lim for dim, lim in zip(item.dim.values(), class_policy["size_limit"])):
            if any(dim > lim for dim, lim in zip([item.dim[k]
                                                  for k in ["height", "width", "depth"]],
                                                 class_policy["size_limit"])):
                return False, "Carry-on bag exceeds size limits."

        return True, "Carry-on luggage complies with the policy."

    def validate_checked_baggage(self, travel_class, checked_items, passenger_type="adult"):
        class_policy = self.classes[travel_class]["checked"].copy()  # Prevent modifications
        fees = 0
        cargo_items = []

        if passenger_type in self.child_allowances:
            child_policy = self.child_allowances[passenger_type]["checked"]
            class_policy["allowance"] += child_policy["allowance"]
            class_policy["weight_limit"] = max(class_policy["weight_limit"], child_policy["weight_limit"])

        for item in checked_items:
            weight = item.weight
            # dimensions = list(item.dim.values())
            dimensions = [value for key, value in item.dim.items() if key != "unit"]
            total_size = sum(dimensions)

            # Check if luggage is over limits and must be in cargo
            if weight > 32 or total_size > 203:
                cargo_items.append(item)

            # Check overweight
            if weight > class_policy["weight_limit"]:
                fees += self.excess_fees["overweight"]

            # Check oversize
            if total_size > class_policy["size_limit"] and total_size <= 203:
                fees += self.excess_fees["oversize"]

        # Check number of items after all weight/size checks
        excess_items = max(0, len(checked_items) - class_policy["allowance"])
        fees += self.excess_fees["extra_piece"] * excess_items

        if cargo_items:
            return False, "Some items must be shipped as cargo due to weight or size.", cargo_items, fees

        return True, "Checked luggage complies with the policy.", cargo_items, fees

    def test_eligibility(self, request):
        carry_on_items = [x for x in request.luggages if x.storage == "carry-on"]
        personal_items = [x for x in request.luggages if x.storage == "personal"]
        checked_items = [x for x in request.luggages if x.storage == "checked"]

        # Validate carry-on
        carry_on_result, carry_on_message = self.validate_carry_on(request.travel_class, carry_on_items, personal_items)
        if not carry_on_result:
            return carry_on_result, carry_on_message, [], 0

        # Validate checked baggage
        checked_result, checked_message, cargo_items, fees = self.validate_checked_baggage(
            request.travel_class, checked_items, request.age_category
        )

        return checked_result, checked_message, cargo_items, fees


def test1():
    # Instantiate the policy
    policy = LuggagePolicy()
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
        self.policy = LuggagePolicy()

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

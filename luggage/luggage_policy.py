class LuggagePolicy:
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

    def validate_carry_on(self, travel_class, carry_on_items, personal_items):
        class_policy = self.classes[travel_class]["carry_on"]

        # Compute total weight of carry-on and personal items
        total_weight = sum(item["weight"] for item in carry_on_items + personal_items)

        # Check quantity
        if len(carry_on_items) + len(personal_items) > class_policy["quantity"] + 1:
            return False, "Exceeded carry-on quantity allowance (including personal items)."

        # Check weight
        if total_weight > class_policy["weight_limit"]:
            return False, "Exceeded carry-on weight limit."

        # Check size
        for item in carry_on_items:
            if any(dim > lim for dim, lim in zip(item["dimensions"], class_policy["size_limit"])):
                return False, "Carry-on bag exceeds size limits."

        return True, "Carry-on luggage complies with the policy."

    def validate_checked_baggage(self, travel_class, checked_items, passenger_type="adult"):
        class_policy = self.classes[travel_class]["checked"]
        fees = 0

        # Adjust for child/infant allowances
        if passenger_type in self.child_allowances:
            class_policy = self.child_allowances[passenger_type]["checked"]

        # Check number of items
        if len(checked_items) > class_policy["allowance"]:
            fees += self.excess_fees["extra_piece"] * (len(checked_items) - class_policy["allowance"])

        for item in checked_items:
            weight, dimensions = item["weight"], item["dimensions"]
            total_size = sum(dimensions)

            # Check weight
            if weight > class_policy["weight_limit"]:
                fees += self.excess_fees["overweight"]

            # Check size
            if total_size > class_policy["size_limit"] and total_size <= 203:
                fees += self.excess_fees["oversize"]

            # Ensure no item exceeds maximum limits
            if weight > 32 or total_size > 203:
                return False, f"Item with weight {weight}kg or size {total_size}cm must be shipped as cargo.", fees

        return True, f"Checked luggage complies with the policy.", fees

    def validate_luggage(self, travel_class, carry_on_items, personal_items, checked_items, passenger_type="adult"):

        # Validate carry-on
        # Stop if not compliant
        carry_on_result, carry_on_message = self.validate_carry_on(travel_class, carry_on_items, personal_items)
        if not carry_on_result:
            return carry_on_result, carry_on_message, 0

        # Validate checked baggage
        checked_result, checked_message, fees = self.validate_checked_baggage(travel_class, checked_items, passenger_type)

        #return f"Luggage complies with the policy. Total fees: ${fees}"
        return checked_result, checked_message, fees

def test1():
    # Instantiate the policy
    policy = LuggagePolicy()
    travel_class = "Economy"

    # Test case: Validate carry-on and checked luggage for Economy class
    carry_on_items = [{"weight": 5, "dimensions": [50, 35, 20]}]  # One carry-on bag
    personal_items = [{"weight": 2, "dimensions": [30, 20, 10]}]  # One personal item
    checked_items = [{"weight": 25, "dimensions": [70, 50, 30]}, {"weight": 50, "dimensions": [70, 50, 30]} ] # One checked bag

    result = policy.validate_luggage(travel_class, carry_on_items, personal_items, checked_items)
    print(result)

def test2():
    # Instantiate the policy
    policy = LuggagePolicy()
    travel_class = "Economy"

    # Test case: Validate carry-on and checked luggage for Economy class
    carry_on_items = [{"weight": 5, "dimensions": [90, 35, 20]}]  # One carry-on bag
    personal_items = [{"weight": 2, "dimensions": [30, 20, 100]}]  # One personal item
    checked_items = [{"weight": 33, "dimensions": [70, 50, 30]}, {"weight": 50, "dimensions": [70, 50, 30]} ] # One checked bag

    result = policy.validate_luggage(travel_class, carry_on_items, personal_items, checked_items)
    print(result)

def test3():
    # Instantiate the policy
    policy = LuggagePolicy()
    travel_class = "Economy"

    # Test case: Validate carry-on and checked luggage for Economy class
    carry_on_items = [{"weight": 1, "dimensions": [20, 35, 20]}]  # One carry-on bag
    personal_items = [{"weight": 5, "dimensions": [30, 20, 30]}]  # One personal item
    checked_items = [{"weight": 13, "dimensions": [70, 50, 30]} ] # One checked bag

    result = policy.validate_luggage(travel_class, carry_on_items, personal_items, checked_items)
    print(result)

def main():

    #test1()
    #test2()
    test3()

if __name__ == "__main__":
    main()





from tester.generic_tester import PolicyTester
import pandas as pd

from luggage_compliance.luggage_compliance import LuggagePolicy


def parse_items(item_str):
    if pd.isna(item_str):
        return []
    items = item_str.split(' | ')
    parsed_items = []
    for item in items:
        weight, dimensions = item.split('kg (')
        weight = float(weight.strip())
        dimensions = list(map(float, dimensions.strip(')').split('x')))
        parsed_items.append({"weight": weight, "dimensions": dimensions})
    return parsed_items


def parse_carry_on_items(item_str):
    if pd.isna(item_str):
        return []
    items = item_str.split(' | ')
    parsed_items = []
    for item in items:
        weight, dimensions = item.split('kg (')
        dimensions = list(map(float, dimensions.strip(')').split('x')))
        parsed_items.append(dimensions)
    return parsed_items


if __name__ == "__main__":
    # Define the configuration for the PolicyTester
    config = {
        'policy_class': LuggagePolicy,
        'csv_file': 'luggage_policy_test_dataset.csv',
        'parse_functions': {
            'carry_on_items': parse_carry_on_items,
            'personal_items': parse_carry_on_items,
            'checked_items': parse_items
        }
    }

    # Instantiate and run the PolicyTester
    tester = PolicyTester(config['policy_class'], config['csv_file'], config['parse_functions'])
    tester.run()

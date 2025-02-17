import json

from luggage import Luggage
from luggage_compliance import LuggageCompliance
from common.generic_tester import PolicyTester
import pandas as pd

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
        'policy_class': LuggageCompliance,
        'csv_file': 'luggage_policy_test_dataset_100.csv',
        'parse_functions': {
            'luggages': lambda x: [Luggage.from_dict(item) for item in json.loads(x)],
            'cargo_items': lambda x: [Luggage.from_dict(item) for item in json.loads(x)] if pd.notnull(x) else []
        }
    }

    # Instantiate and run the PolicyTester
    tester = PolicyTester(config['policy_class'], config['csv_file'], config['parse_functions'])
    tester.run()

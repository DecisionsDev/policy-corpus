import sys
import os

from custom_evaluators import cargo_items_evaluator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from luggage import Luggage
from luggage_compliance import LuggageCompliance
from common.generic_tester import PolicyTester
import json
import pandas as pd


# Examples of parsing functions
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
            'moved_to_checked': lambda x: [Luggage.from_dict(item) for item in json.loads(x)] if pd.notnull(x) and len(
                x) > 0 else [],
            'cargo_items': lambda x: [Luggage.from_dict(item) for item in json.loads(x)] if pd.notnull(x) and len(x) > 0 else []
        },
        'eval_columns': ["compliance_result", "compliance_message", "moved_to_checked", "cargo_items", "fees"],
        'evaluators': [cargo_items_evaluator]
    }

    # Instantiate and run the tester
    tester = PolicyTester(
        config['policy_class'],
        config['csv_file'],
        config.setdefault('parse_functions', None),
        config.setdefault('eval_columns', None),
        config.setdefault('evaluators', None)
    )
    tester.run()

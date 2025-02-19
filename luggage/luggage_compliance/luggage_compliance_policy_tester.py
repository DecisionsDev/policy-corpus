import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from luggage import Luggage
from luggage_compliance import LuggageCompliance
from common.generic_tester import PolicyTester
import pandas as pd

import json


# Example of the evaluator function
def cargo_items_evaluator(data, results_transposed):
    """Evaluate cargo_items column by parsing JSON and comparing lists as sets."""
    column = "cargo_items"  # The column we're evaluating
    if column not in data.columns:
        print(f"Skipping {column} evaluation - column not found in data.")
        return

    y_true = data[column]
    y_pred = results_transposed[2]  # Match column index

    if len(y_pred) != len(y_true):
        print(f"Skipping {column} evaluation due to size mismatch.")
        return

    def parse_json(value):
        """Safely parse JSON to list, return empty list on failure."""
        try:
            return json.loads(value) if isinstance(value, str) else value
        except json.JSONDecodeError:
            return []

    # Parse JSON strings into Python lists
    y_true_parsed = [set(parse_json(item)) for item in y_true]
    y_pred_parsed = [set(parse_json(item)) for item in y_pred]

    # Compare sets and calculate accuracy
    matches = sum(1 for true_val, pred_val in zip(y_true_parsed, y_pred_parsed) if true_val == pred_val)
    accuracy = matches / len(y_true)

    print(f"Cargo Items Accuracy: {accuracy:.2f}")


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
            'cargo_items': lambda x: [Luggage.from_dict(item) for item in json.loads(x)] if pd.notnull(x) else []
        },
        'eval_columns': ["compliance_result", "compliance_message", "cargo_items", "fees"],
        'evaluators': [cargo_items_evaluator]
    }

    # Instantiate and run the tester
    tester = PolicyTester(config['policy_class'], config['csv_file'], config['parse_functions'], config['eval_columns'], config.setdefault('evaluators', None))
    tester.run()

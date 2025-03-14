import argparse
import json
from typing import Dict

import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def benchmark_results(resulting_file, column_mapping: Dict[str, str]) -> Dict[str, Dict[str, float | int]]:
    print("Starting the benchmarking...")

    # Load JSON file
    with open(resulting_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract test case and generated answer values
    test_case_values = []
    generated_values = []

    for key, item in data.items():
        test_case_entry = item["test_case"]
        generated_entry = item["generated_answer"]

        row_test_case = []
        row_generated = []

        for test_case_col, generated_col in column_mapping.items():
            row_test_case.append(test_case_entry.get(test_case_col))
            row_generated.append(generated_entry.get(generated_col))

        test_case_values.append(row_test_case)
        generated_values.append(row_generated)

    # Convert to DataFrame
    df_test_case = pd.DataFrame(test_case_values, columns=column_mapping.keys())
    df_generated = pd.DataFrame(generated_values, columns=column_mapping.keys())

    # Calculate metrics for each column
    metrics = {}
    for col in column_mapping.keys():
        y_true = df_test_case[col]
        y_pred = df_generated[col]

        # Convert categorical values to strings for comparison
        if not pd.api.types.is_numeric_dtype(y_true) or not pd.api.types.is_numeric_dtype(y_pred):
            y_true = y_true.astype(str)
            y_pred = y_pred.astype(str)

        # Compute metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

        metrics[col] = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1
        }

    return metrics


def parse_column_mapping(value):
    """
    Parses the column_mapping argument, which should be a JSON string.
    Example input: '{"eligibility": "elig", "price": "cost"}'
    """
    if not value:
        return {}  # Return empty dict if not provided

    try:
        return json.loads(value)  # Convert JSON string to dictionary
    except json.JSONDecodeError:
        raise ValueError("Invalid format for column_mapping. Must be a valid JSON string.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate the benchmarking metrics from the resulting json")
    parser.add_argument("--output_file", type=str, required=True, help="The path for the benchmarking results output")
    parser.add_argument("--column_mapping", type=str, required=True,
                        help="JSON string for column name mapping for benchmark metrics calculation (e.g., '{\"eligibility\": \"elig\"}').")

    args = parser.parse_args()

    column_mapping = parse_column_mapping(args.column_mapping)
    if column_mapping:
        res = benchmark_results(args.output_file, column_mapping)
        print(res)
    else:
        print("Something went wrong during column mapping")

# python ./benchmarking_results.py --output_file "generation_result_test.json" --column_mapping '{"eligibility": "eligible"}'

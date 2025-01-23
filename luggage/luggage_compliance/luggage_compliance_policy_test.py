import pprint
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
import time

from luggage_compliance.luggage_compliance_pricing import LuggagePolicy

# Prepare the data
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
    # Load the CSV file
    csv_file = 'luggage-compliance-pricing-requests-dataset.csv'
    data = pd.read_csv(csv_file)

    # Initialize the LuggagePolicy class
    policy = LuggagePolicy()

    # Apply the parsing functions to the dataframe
    data['carry_on_items'] = data['carry_on_items'].apply(parse_carry_on_items)
    data['personal_items'] = data['personal_items'].apply(parse_carry_on_items)
    data['checked_items'] = data['checked_items'].apply(parse_items)

    # Initialize lists to store results
    carry_on_results = []
    carry_on_messages = []
    checked_results = []
    checked_messages = []
    fees = []
    execution_times = []

    # Iterate through the dataframe and validate each row
    for index, row in data.iterrows():
        travel_class = row['travel_class']
        passenger_type = row['passenger_type']
        carry_on_weight = row['carry_on_weight']
        carry_on_items = row['carry_on_items']
        personal_items = row['personal_items']
        checked_items = row['checked_items']

        # Validate carry-on items
        start_time = time.time()
        carry_on_result, carry_on_message = policy.validate_carry_on(travel_class, carry_on_items, personal_items, carry_on_weight)
        execution_time = time.time() - start_time

        # Validate checked items
        res = policy.validate_checked_baggage(travel_class, checked_items, passenger_type)
        checked_result = res[0]

        # Store results
        carry_on_results.append(carry_on_result)
        carry_on_messages.append(carry_on_message)
        checked_results.append(checked_result)
        execution_times.append(execution_time)

    # Calculate metrics
    y_true = data['eligible']
    y_pred = [a and b for a, b in zip(carry_on_results, checked_results)]

    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    average_execution_time = np.array(execution_times).mean()

    # Print metrics
    print(f"Accuracy: {accuracy}")
    print(f"F1 Score: {f1}")
    print(f"Recall: {recall}")
    print(f"Precision: {precision}")
    print(f"Average Execution Time for validate_carry_on: {average_execution_time} seconds")

    diff_indices = np.where(y_true != y_pred)[0]

    for el in diff_indices:
        print("Case:\n----------")
        pprint.pprint(data.loc[el])
        print("---------\n")
        print(f"True value: {y_true[el]}\nPredicted: {y_pred[el]}, Carry on: {carry_on_results[el]}, "
              f"Checked: {checked_results[el]}, Message: {checked_messages[el]}")
        print("=========\n")


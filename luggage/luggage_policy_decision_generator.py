import random
import pandas as pd
import numpy as np
import json

from luggage_policy import LuggagePolicy

# Instantiate the policy
policy = LuggagePolicy()

def generate_carry_on_weight(mean=8, std_dev=10):
    # Ensure weight are non-negative and rounded to 2 decimal places
    w = np.random.normal(mean, std_dev)
    weight = max(0, w)
    
    return weight

def generate_random_request():
    travel_class = random.choice(["Economy", "Business", "First"])
    passenger_type = random.choices(
        ["adult", "child", "infant"],  # Passenger categories
        weights=[75, 20, 5],          # Respective probabilities
        k=1                           # Number of samples to generate
    )[0]

    # Generate carry-on items
    num_carry_on = random.randint(0, 2)
    carry_on_items = [
         {
        "weight": round(generate_carry_on_weight(2, 10)),
        "dimensions": [random.randint(20, 50), random.randint(20, 40), random.randint(10, 30)],
        }
        for _ in range(num_carry_on)
    ]

    num_personal_items = random.choices(
        [0, 1, 2],  # Possible numbers of checked items
        weights=[50, 30, 20],  # Respective probabilities
        k=1  # Number of samples to generate
    )[0]
    personal_items = [
        {
        "weight": round(generate_carry_on_weight(3, 30)),
        "dimensions": [random.randint(50, 90), random.randint(30, 70), random.randint(20, 50)],
        }
        for _ in range(num_personal_items)
    ]

    # Generate checked items
    num_checked_items = random.choices(
        [0, 1, 2, 3, 4],  # Possible numbers of checked items
        weights=[50, 30, 15, 4, 1],  # Respective probabilities
        k=1  # Number of samples to generate
    )[0]
    checked_items = [
        {
            "weight": round(generate_carry_on_weight(12, 20)),
            "dimensions": [random.randint(50, 100), random.randint(30, 80), random.randint(20, 50)],
        }
        for _ in range(num_checked_items)
    ]

    return travel_class, carry_on_items, personal_items,checked_items, passenger_type

# Function to rename keys
def rename_keys(item, mapping):
    return {mapping.get(k, k): v for k, v in item.items()}

def write_luggages(luggages):
    # Define key mapping
    key_mapping = {'weight': 'w', 'dimensions': 'dim'}

    # Rename keys for all items
    renamed_luggages = [rename_keys(luggage, key_mapping) for luggage in luggages]

    # Serialize to JSON with indentation
    json_str = renamed_luggages
    #json_str = json.dumps(renamed_luggages, indent=0)

    return json_str

def generate_decisions(n):
    results = []
    for _ in range(n):
        travel_class, carry_on_items, personal_items, checked_items, passenger_type = generate_random_request()
        compliance, message, fees = policy.validate_luggage(
            travel_class, carry_on_items, personal_items, checked_items, passenger_type
        )

        results.append({
            "travel_class": travel_class,
            "carry_on_items": write_luggages(carry_on_items),
            "personal_items":  write_luggages(personal_items), #"carry_on_weight": carry_on_weight,
            "checked_items":  write_luggages(checked_items),
            "passenger_type": passenger_type,
            "compliance": compliance,
            "reason": message,
            "fees": fees
        })

    return results

def format_data_units(n):
    nb_units = round(n / 1000000)
    if nb_units >= 1:
        unit = "M"
    else: 
        nb_units = round(n / 1000)
        if nb_units >= 1:
            unit = "K"
        else:
            nb_units = n
            unit = ""
    
    label = f'{nb_units}{unit}'
    return label

def generate(n):

    # Generate the requests and their results
    data = generate_decisions(n)

    # Convert to a Pandas DataFrame
    df = pd.DataFrame(data)

    # Save DataFrame to CSV
    data_units = format_data_units(n)
    output_file = "luggage/luggage_policy_decisions_" + data_units + ".csv"
    df.to_csv(output_file, index=False)

    print(f"Generated {n} luggage requests and saved to {output_file}.")

def main():
    generate(100)
    generate(1000)
    generate(10000)
    generate(10000)

if __name__ == "__main__":
    main()

import pandas as pd
import numpy as np


columns = [
    'applicant_age',
    'has_valid_license',
    'vehicle_registered',
    'vehicle_age',
    'clean_driving_record',
    'prior_insurance_coverage',
    'resides_in_country',
    'credit_score',
    'vehicle_usage',
    'minimum_liability_coverage',
    'eligibility'
]


def determine_eligibility(row):
    if row['applicant_age'] < 18 or row['applicant_age'] > 75:
        return False
    if not row['has_valid_license']:
        return False
    if not row['vehicle_registered']:
        return False
    if row['vehicle_age'] > 20:
        return False
    if not row['clean_driving_record']:
        return False
    if not row['prior_insurance_coverage']:
        return False
    if not row['resides_in_country']:
        return False
    if row['credit_score'] < 500:
        return False
    if row['vehicle_usage'] != 'personal':
        return False
    if not row['minimum_liability_coverage']:
        return False
    return True


def generate_test_dataset(num_samples=100):
    # Generate data
    data = {
        'applicant_age': np.random.randint(16, 85, num_samples),
        'has_valid_license': np.random.choice([True, False], num_samples),
        'vehicle_registered': np.random.choice([True, False], num_samples),
        'vehicle_age': np.random.randint(0, 30, num_samples),
        'clean_driving_record': np.random.choice([True, False], num_samples),
        'prior_insurance_coverage': np.random.choice([True, False], num_samples),
        'resides_in_country': np.random.choice([True, False], num_samples),
        'credit_score': np.random.randint(300, 850, num_samples),
        'vehicle_usage': np.random.choice(['personal', 'commercial', 'rideshare'], num_samples),
        'minimum_liability_coverage': np.random.choice([True, False], num_samples)
    }

    df = pd.DataFrame(data)
    df['eligibility'] = df.apply(determine_eligibility, axis=1)

    # Ensure at least 40% of the values in the 'eligibility' column are different
    eligible_count = df['eligibility'].sum()
    ineligible_count = num_samples - eligible_count

    if eligible_count < 0.4 * num_samples:
        num_to_change = int(0.4 * num_samples - eligible_count)
        ineligible_indices = df[df['eligibility'] == False].index
        change_indices = np.random.choice(ineligible_indices, num_to_change, replace=False)
        df.loc[change_indices, 'eligibility'] = True
    elif ineligible_count < 0.4 * num_samples:
        num_to_change = int(0.4 * num_samples - ineligible_count)
        eligible_indices = df[df['eligibility'] == True].index
        change_indices = np.random.choice(eligible_indices, num_to_change, replace=False)
        df.loc[change_indices, 'eligibility'] = False

    return df

df = generate_test_dataset(num_samples=100)

df.to_csv('insurance_eligibility_dataset.csv', index=False)

print("CSV dataset generated successfully.")

import pandas as pd
import numpy as np

from common.DataGenerator import DataGenerator


class InsuranceEligibilityDataGenerator(DataGenerator):
    COLUMN_NAMES = [
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

    def determine_eligibility(self, row):
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

    def generate_test_dataset(self, num_samples=100):
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
        df['eligibility'] = df.apply(self.determine_eligibility, axis=1)

        eligible_count = df['eligibility'].sum()
        ineligible_count = num_samples - eligible_count

        while eligible_count < 0.4 * num_samples or ineligible_count < 0.4 * num_samples:
            additional_data = {
                'applicant_age': np.random.randint(18, 75, 10),
                'has_valid_license': [True] * 10,
                'vehicle_registered': [True] * 10,
                'vehicle_age': np.random.randint(0, 20, 10),
                'clean_driving_record': [True] * 10,
                'prior_insurance_coverage': [True] * 10,
                'resides_in_country': [True] * 10,
                'credit_score': np.random.randint(500, 850, 10),
                'vehicle_usage': ['personal'] * 10,
                'minimum_liability_coverage': [True] * 10
            }

            additional_df = pd.DataFrame(additional_data)
            additional_df['eligibility'] = additional_df.apply(self.determine_eligibility, axis=1)

            df = pd.concat([df, additional_df], ignore_index=True)

            eligible_count = df['eligibility'].sum()
            ineligible_count = len(df) - eligible_count

        df = df.sample(n=num_samples, random_state=1).reset_index(drop=True)

        return df


if __name__ == "__main__":
    generator = InsuranceEligibilityDataGenerator()
    df = generator.generate_test_dataset(num_samples=100)

    df.to_csv('insurance_eligibility_dataset.csv', index=False)

    print("CSV dataset generated successfully.")

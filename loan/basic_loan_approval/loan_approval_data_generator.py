import random

import pandas as pd

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from common.generic_data_generator import DataGenerator


class LoanApprovalDataGenerator(DataGenerator):
    COLUMN_NAMES = [
        'age',
        'residency',
        'credit_score',
        'annual_income',
        'employment_status',
        'dti',
        'loan_amount',
        'eligibility'
    ]

    def determine_eligibility(self, row):
        if row['age'] < 18:
            return False
        if row['residency'] not in ['citizen', 'resident']:
            return False
        if row['credit_score'] < 600:
            return False
        if row['annual_income'] < 30000:
            return False
        if row['employment_status'] == 'unemployed':
            return False
        if row['dti'] > 0.40:
            return False
        if not (5000 <= row['loan_amount'] <= 50000):
            return False
        return True
    def generate_test_dataset(self, num_samples=100):
        data = []
        eligible_count = 0
        non_eligible_count = 0

        while len(data) < num_samples:
            age = random.randint(18, 80)
            residency = random.choice(['citizen', 'resident', 'foreigner'])
            credit_score = random.randint(300, 850)
            annual_income = random.randint(20000, 100000)
            employment_status = random.choice(['employed', 'self-employed', 'unemployed'])
            dti = round(random.uniform(0.05, 0.60), 2)  # Debt-to-Income Ratio
            loan_amount = random.randint(1000, 60000)

            row = {
                'age': age,
                'residency': residency,
                'credit_score': credit_score,
                'annual_income': annual_income,
                'employment_status': employment_status,
                'dti': dti,
                'loan_amount': loan_amount
            }
            eligibility = self.determine_eligibility(row)

            if eligibility:
                eligible_count += 1
            else:
                non_eligible_count += 1

            row['eligibility'] = eligibility
            data.append(row)

            # Ensure at least 40% of both eligible and non-eligible entries
            if eligible_count >= 0.4 * num_samples and non_eligible_count >= 0.4 * num_samples:
                break

        # If we don't have enough eligible or non-eligible entries, adjust the dataset
        if eligible_count < 0.4 * num_samples:
            while eligible_count < 0.4 * num_samples:
                age = random.randint(18, 80)
                residency = random.choice(['citizen', 'resident'])
                credit_score = random.randint(600, 850)
                annual_income = random.randint(30000, 100000)
                employment_status = random.choice(['employed', 'self-employed'])
                dti = round(random.uniform(0.05, 0.40), 2)  # Debt-to-Income Ratio
                loan_amount = random.randint(5000, 50000)

                row = {
                    'age': age,
                    'residency': residency,
                    'credit_score': credit_score,
                    'annual_income': annual_income,
                    'employment_status': employment_status,
                    'dti': dti,
                    'loan_amount': loan_amount
                }
                eligibility = self.determine_eligibility(row)

                if eligibility:
                    eligible_count += 1
                    row['eligibility'] = eligibility
                    data.append(row)

        if non_eligible_count < 0.4 * num_samples:
            while non_eligible_count < 0.4 * num_samples:
                age = random.randint(18, 80)
                residency = random.choice(['foreigner'])
                credit_score = random.randint(300, 599)
                annual_income = random.randint(20000, 29999)
                employment_status = 'unemployed'
                dti = round(random.uniform(0.41, 0.60), 2)  # Debt-to-Income Ratio
                loan_amount = random.choice([1000, 60000])

                row = {
                    'age': age,
                    'residency': residency,
                    'credit_score': credit_score,
                    'annual_income': annual_income,
                    'employment_status': employment_status,
                    'dti': dti,
                    'loan_amount': loan_amount
                }
                eligibility = self.determine_eligibility(row)

                if not eligibility:
                    non_eligible_count += 1
                    row['eligibility'] = eligibility
                    data.append(row)

        return pd.DataFrame(data)


if __name__ == "__main__":
    generator = LoanApprovalDataGenerator()

    data = generator.generate_test_dataset()
    # Write the data to a CSV file
    data.to_csv('basic_loan_approval_dataset.csv', index=False)

    print("Test dataset generated and saved to 'basic_loan_approval_dataset.csv'")

import csv
import random

fields = ['age', 'residency', 'credit_score', 'annual_income', 'employment_status', 'dti', 'loan_amount', 'eligibility']


def check_eligibility(age, residency, credit_score, annual_income, employment_status, dti, loan_amount):
    if age < 18:
        return False
    if residency not in ['citizen', 'resident']:
        return False
    if credit_score < 600:
        return False
    if annual_income < 30000:
        return False
    if employment_status == 'unemployed':
        return False
    if dti > 0.40:
        return False
    if not (5000 <= loan_amount <= 50000):
        return False
    return True


def generate_test_dataset(num_samples=100):
    # Generate the data
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

        eligibility = check_eligibility(age, residency, credit_score, annual_income, employment_status, dti, loan_amount)

        if eligibility:
            eligible_count += 1
        else:
            non_eligible_count += 1

        data.append([age, residency, credit_score, annual_income, employment_status, dti, loan_amount, eligibility])

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

            eligibility = check_eligibility(age, residency, credit_score, annual_income, employment_status, dti, loan_amount)

            if eligibility:
                eligible_count += 1
                data.append([age, residency, credit_score, annual_income, employment_status, dti, loan_amount, eligibility])

    if non_eligible_count < 0.4 * num_samples:
        while non_eligible_count < 0.4 * num_samples:
            age = random.randint(18, 80)
            residency = random.choice(['foreigner'])
            credit_score = random.randint(300, 599)
            annual_income = random.randint(20000, 29999)
            employment_status = 'unemployed'
            dti = round(random.uniform(0.41, 0.60), 2)  # Debt-to-Income Ratio
            loan_amount = random.choice([1000, 60000])

            eligibility = check_eligibility(age, residency, credit_score, annual_income, employment_status, dti, loan_amount)

            if not eligibility:
                non_eligible_count += 1
                data.append([age, residency, credit_score, annual_income, employment_status, dti, loan_amount, eligibility])

    return data

if __name__ == "__main__":
    data = generate_test_dataset()
    # Write the data to a CSV file
    with open('basic_loan_approval_dataset.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows(data)

    print("Test dataset generated and saved to 'basic_loan_approval_dataset.csv'")

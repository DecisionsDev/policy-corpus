import pandas as pd
from faker import Faker
from datetime import date, timedelta
import random
from acme_time_off import Employee, Request  # Import Employee and Request classes

# Initialize Faker
fake = Faker()

# Helper functions to generate random dates and employee types
def random_hire_date():
    # Generate a random hire date in the past 30 years
    start_date = date.today() - timedelta(days=30 * 365)
    return start_date + timedelta(days=random.randint(0, 30 * 365))

def random_employment_type():
    return random.choice(["regular full-time", "part-time", "contractor", "supplemental"])

def random_request_date():
    # Generate a random request date within the past year
    start_date = date.today() - timedelta(days=365)
    return start_date + timedelta(days=random.randint(0, 365))

def generate_data(nb):
    # Generate test dataset
    test_data = []
    for i in range(nb):
        # Generate random employee attributes
        name = fake.name()
        employment_type = random_employment_type()
        hire_date = random_hire_date()
        supplemental = employment_type == "supplemental"
        request_date = random_request_date()

        # Define parameters to test edge cases
        if i < 10:
            # Specific cases for edge testing
            if i % 2 == 0:
                hire_date = request_date - timedelta(days=10 * 365)  # Exactly 10 years
            else:
                hire_date = request_date - timedelta(days=20 * 365)  # Exactly 20 years
            employment_type = "regular full-time"
        elif i < 20:
            # Supplemental employees
            employment_type = "supplemental"
        elif i < 30:
            # Part-time employees
            employment_type = "part-time"
        elif i < 40:
            # Newly hired employees
            hire_date = request_date - timedelta(days=random.randint(1, 60))  # Within the last 60 days
            employment_type = "regular full-time"

        # Create Employee and Request instances
        employee = Employee(name, employment_type, hire_date, supplemental)
        request = Request(employee, reference_date=request_date)

        # Append both input data and calculated outcomes
        test_data.append({
            "name": employee.name,
            "employment_type": employee.employment_type,
            "hire_date": employee.hire_date,
            "supplemental": employee.supplemental,
            "request_date": request_date
        })

    # Convert to DataFrame
    test_df = pd.DataFrame(test_data)

    # Save dataset to CSV
    test_df.to_csv(f'human-resources/acme_time_off_requests_{nb}.csv', index=False)

    # Optional: Display the dataset to the user
    # import ace_tools as tools; tools.display_dataframe_to_user(name="Employee Test Dataset with Policy Outcomes", dataframe=test_df)

if __name__ == "__main__":
    # Generate data for 1000 employees
    generate_data(nb=1000)

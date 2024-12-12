import pandas as pd
from acme_time_off import Employee, Request

def process_employee_dataset(input_file, output_file):
    # Read the dataset and parse the relevant dates
    dataset = pd.read_csv(input_file, parse_dates=['hire_date', 'request_date'])

    # Ensure hire_date and request_date are converted to datetime.date
    dataset['hire_date'] = dataset['hire_date'].dt.date
    dataset['request_date'] = dataset['request_date'].dt.date

    results = []

    for _, row in dataset.iterrows():
        # Create Employee instance
        employee = Employee(
            name=row['name'],
            employment_type=row['employment_type'],
            hire_date=row['hire_date'],
            supplemental=row['supplemental']
        )

        # Create Request instance with the request_date as reference_date
        request = Request(employee=employee, reference_date=row['request_date'])

        # Append both input data and calculated outcomes
        results.append({
            "name": row['name'],
            "employment_type": row['employment_type'],
            "hire_date": row['hire_date'],
            "supplemental": row['supplemental'],
            "request_date": row['request_date'],
            "years_of_service": request.years_of_service,
            "fixed_holidays": len(request.fixed_holidays),
            "personal_choice_holidays": request.personal_choice_holidays,
            "vacation_weeks": request.vacation_weeks,
            "pst_hours": request.pst_hours,
            "total_time_off_days": request.calculate_total_time_off()
        })

    # Convert results to a DataFrame and save to CSV
    processed_dataset = pd.DataFrame(results)
    processed_dataset.to_csv(output_file, index=False)

if __name__ == "__main__":
    # Process the dataset and save decisions to a new file
    process_employee_dataset(
        'human-resources/acme_time_off_requests_1000.csv',
        'human-resources/acme_time_off_decisions_1000.csv'
    )

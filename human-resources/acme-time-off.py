from datetime import date, timedelta

class Employee:
    def __init__(self, name, employment_type, hire_date, supplemental=False):
        self.name = name
        self.employment_type = employment_type.lower()  # 'regular full-time' or others
        self.hire_date = hire_date  # date object
        self.supplemental = supplemental
        self.years_of_service = self.calculate_years_of_service()
        self.fixed_holidays = self.get_fixed_holidays()
        self.personal_choice_holidays = self.calculate_personal_choice_holidays()
        self.vacation_weeks = self.calculate_vacation_weeks()
        self.pst_hours = self.calculate_pst_hours()

    def calculate_years_of_service(self):
        today = date.today()
        delta = today - self.hire_date
        return delta.days // 365  # Approximate years of service

    def get_fixed_holidays(self):
        if self.employment_type == 'regular full-time':
            return [
                "New Year’s Day",
                "Martin Luther King Jr. Day",
                "Memorial Day",
                "Independence Day",
                "Labor Day",
                "Thanksgiving Day",
                "Day after Thanksgiving",
                "Christmas Day"
            ]
        else:
            return []

    def calculate_personal_choice_holidays(self):
        if self.employment_type == 'regular full-time' and not self.supplemental:
            return 4  # days
        else:
            return 0

    def calculate_vacation_weeks(self):
        if self.employment_type != 'regular full-time':
            return 0
        if self.years_of_service < 10:
            return 3
        elif 10 <= self.years_of_service < 20:
            return 4
        elif self.years_of_service >= 20:
            if self.hire_date < date(2004, 1, 1):
                return 5
            else:
                return 4
        else:
            return 0  # Default to 0 weeks if criteria not met

    def calculate_pst_hours(self):
        if self.employment_type != 'regular full-time':
            return 0
        total_pst_hours = 48  # 6 days * 8 hours
        # Pro-rate for new hires
        current_year = date.today().year
        if self.hire_date.year == current_year:
            days_worked = (date.today() - self.hire_date).days
            total_days_in_year = 366 if self.is_leap_year(current_year) else 365
            prorated_pst = (days_worked / total_days_in_year) * total_pst_hours
            return round(prorated_pst, 2)
        else:
            return total_pst_hours

    @staticmethod
    def is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def display_time_off_policies(self):
        print(f"Time Off Policies for {self.name}:")
        print(f"Years of Service: {self.years_of_service}")
        print(f"Employment Type: {self.employment_type.capitalize()}")
        print(f"Supplemental: {'Yes' if self.supplemental else 'No'}")
        print(f"Fixed Holidays: {', '.join(self.fixed_holidays) if self.fixed_holidays else 'None'}")
        print(f"Personal Choice Holidays: {self.personal_choice_holidays} days")
        print(f"Vacation: {self.vacation_weeks} weeks per year")
        print(f"Personal Sick Time (PST): {self.pst_hours} hours per year")
        print("Note: Unused PST cannot be carried over or paid out.")

# Test cases to cover all branches
if __name__ == "__main__":
    test_employees = [
        # Employee hired before 2004 with over 20 years of service
        {
            "name": "Alice Johnson",
            "employment_type": "regular full-time",
            "hire_date": date(1995, 5, 20),
            "supplemental": False
        },
        # New hire this year (pro-rated PST)
        {
            "name": "Bob Smith",
            "employment_type": "regular full-time",
            "hire_date": date(date.today().year, 8, 15),
            "supplemental": False
        },
        # Supplemental employee (no personal choice holidays)
        {
            "name": "Carol Williams",
            "employment_type": "regular full-time",
            "hire_date": date(2010, 3, 10),
            "supplemental": True
        },
        # Part-time employee (no benefits)
        {
            "name": "David Lee",
            "employment_type": "part-time",
            "hire_date": date(2012, 6, 1),
            "supplemental": False
        },
        # Employee with exactly 10 years of service
        {
            "name": "Eva Green",
            "employment_type": "regular full-time",
            "hire_date": date(date.today().year - 10, date.today().month, date.today().day),
            "supplemental": False
        },
        # Employee with exactly 20 years of service, hired after Jan 1, 2004
        {
            "name": "Frank Harris",
            "employment_type": "regular full-time",
            "hire_date": date(2004, 10, 14),  # Adjust date to ensure 20 years
            "supplemental": False
        },
        # Employee with less than 10 years of service
        {
            "name": "Grace Kim",
            "employment_type": "regular full-time",
            "hire_date": date(date.today().year - 5, 1, 1),
            "supplemental": False
        },
        # Employee hired today (zero years of service)
        {
            "name": "Henry Brown",
            "employment_type": "regular full-time",
            "hire_date": date.today(),
            "supplemental": False
        },
        # Employee with hire date in a leap year
        {
            "name": "Isabella Davis",
            "employment_type": "regular full-time",
            "hire_date": date(2016, 2, 29),
            "supplemental": False
        },
        # Non-regular full-time employee who is supplemental
        {
            "name": "Jack Wilson",
            "employment_type": "contractor",
            "hire_date": date(2018, 4, 15),
            "supplemental": True
        }
    ]

    for emp_info in test_employees:
        employee = Employee(
            name=emp_info["name"],
            employment_type=emp_info["employment_type"],
            hire_date=emp_info["hire_date"],
            supplemental=emp_info["supplemental"]
        )
        employee.display_time_off_policies()
        print("-" * 60)

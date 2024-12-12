from datetime import date, timedelta

class Employee:
    def __init__(self, name, employment_type, hire_date, supplemental=False):
        self.name = name
        self.employment_type = employment_type.lower()  # 'regular full-time' or others
        self.hire_date = hire_date  # date object
        self.supplemental = supplemental

class Request:
    def __init__(self, employee, reference_date=None):
        self.employee = employee
        self.reference_date = reference_date or date.today()  # Use provided reference date or default to today
        self.years_of_service = self.calculate_years_of_service()
        self.fixed_holidays = self.get_fixed_holidays()
        self.personal_choice_holidays = self.calculate_personal_choice_holidays()
        self.vacation_weeks = self.calculate_vacation_weeks()
        self.pst_hours = self.calculate_pst_hours()

    def calculate_years_of_service(self):
        delta = self.reference_date - self.employee.hire_date
        return delta.days // 365  # Approximate years of service

    def get_fixed_holidays(self):
        if self.employee.employment_type == 'regular full-time':
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
        if self.employee.employment_type == 'regular full-time' and not self.employee.supplemental:
            return 4  # days
        else:
            return 0

    def calculate_vacation_weeks(self):
        if self.employee.employment_type != 'regular full-time':
            return 0
        if self.years_of_service < 10:
            return 3
        elif 10 <= self.years_of_service < 20:
            return 4
        elif self.years_of_service >= 20:
            if self.employee.hire_date < date(2004, 1, 1):
                return 5
            else:
                return 4
        else:
            return 0

    def calculate_pst_hours(self):
        if self.employee.employment_type != 'regular full-time':
            return 0
        total_pst_hours = 48  # 6 days * 8 hours
        current_year = self.reference_date.year
        if self.employee.hire_date.year == current_year:
            days_worked = (self.reference_date - self.employee.hire_date).days
            total_days_in_year = 366 if self.is_leap_year(current_year) else 365
            prorated_pst = (days_worked / total_days_in_year) * total_pst_hours
            return round(prorated_pst, 2)
        else:
            return total_pst_hours

    @staticmethod
    def is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def calculate_total_time_off(self):
        fixed_holiday_days = len(self.fixed_holidays)
        personal_choice_holiday_days = self.personal_choice_holidays
        vacation_days = self.vacation_weeks * 5
        pst_days = self.pst_hours / 8
        return round(fixed_holiday_days + personal_choice_holiday_days + vacation_days + pst_days, 2)

    def display_time_off_policies(self):
        print(f"Time Off Policies for {self.employee.name}:")
        print(f"Years of Service: {self.years_of_service}")
        print(f"Employment Type: {self.employee.employment_type.capitalize()}")
        print(f"Supplemental: {'Yes' if self.employee.supplemental else 'No'}")
        print(f"Fixed Holidays: {', '.join(self.fixed_holidays) if self.fixed_holidays else 'None'}")
        print(f"Personal Choice Holidays: {self.personal_choice_holidays} days")
        print(f"Vacation: {self.vacation_weeks} weeks per year")
        print(f"Personal Sick Time (PST): {self.pst_hours} hours per year")
        print(f"Total Time Off: {self.calculate_total_time_off()} days")
        print("Note: Unused PST cannot be carried over or paid out.")

# Test cases to cover all branches
if __name__ == "__main__":
    reference_date = date(2024, 1, 1)  # Fixed reference date for consistency
    test_employees = [
        Employee("Alice Johnson", "regular full-time", date(1995, 5, 20), False),
        Employee("Bob Smith", "regular full-time", date(reference_date.year, 8, 15), False),
        Employee("Carol Williams", "regular full-time", date(2010, 3, 10), True),
        Employee("David Lee", "part-time", date(2012, 6, 1), False),
        Employee("Eva Green", "regular full-time", date(reference_date.year - 10, reference_date.month, reference_date.day), False),
        Employee("Frank Harris", "regular full-time", date(2004, 10, 14), False),
        Employee("Grace Kim", "regular full-time", date(reference_date.year - 5, 1, 1), False),
        Employee("Henry Brown", "regular full-time", reference_date, False),
        Employee("Isabella Davis", "regular full-time", date(2016, 2, 29), False),
        Employee("Jack Wilson", "contractor", date(2018, 4, 15), True),
    ]

    for employee in test_employees:
        # Create a Request instance with the Employee object
        request = Request(employee=employee, reference_date=reference_date)
        # Call display_time_off_policies on the Request instance
        request.display_time_off_policies()
        print("-" * 60)

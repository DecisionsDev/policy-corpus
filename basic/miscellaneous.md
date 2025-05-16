# Unit tests

## 📆 Time Off / Leave Policy
### Policy:
An employee is eligible for paid vacation if they have worked more than 6 months and have not taken vacation in the past 30 days.

### Tests:
- Rule chaining: two conditions (employment duration + last vacation date).
- Date comparison logic.
- Negation handling ("have not taken").

## 🛍️ Discount Eligibility Policy
### Policy:
A customer receives a 10% discount if they are a loyalty member and have made at least 5 purchases in the last 3 months.

### Tests:
- Numeric thresholds.
- Logical AND.
- Temporal window filtering (last 3 months).

## 🚗 Car Rental Policy
### Policy:
A driver may rent a car if they are over 21 and hold a valid license.

### Tests:
- Comparison (> 21).
- Boolean flags (license validity).
- Simple eligibility gates.

## 🛂 Travel Reimbursement Policy
### Policy:
Travel expenses are reimbursed if pre-approved by a manager and the total cost is under $1,000.

### Tests:
- Conditional requirement ("if pre-approved").
- Budget constraint.
- Multi-condition fulfillment.

## 🏥 Health Insurance Claim Policy
### Policy:
A claim is approved if it is submitted within 90 days of the treatment date and the procedure is covered.

### Tests:
- Time delta calculation.
- Lookup/membership in a set (covered procedures).
- AND condition.

## 🧾 Expense Approval Policy
### Policy:
Expenses under $100 can be auto-approved; above $100 require manager approval.

### Tests:
- Conditional branching.
- Threshold logic with inequality.
- Rule fallback/escalation.

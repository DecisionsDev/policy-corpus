# Car insurance compliance and preliminary fee policy 


## Policy
This loan approval and interest rate policy outlines the requirements for the approval or rejection of loan applications for customers in the United States to ensure consistency and mitigate risk.
This policy applies to all individual loan applications submitted to Acme car Insurance within the United States.
[The policy in plain text](basic_loan_approval_us.txt)

## Code
Associated code contains:
- [a reference implementation of the policy in Python](loan_compliance/loan_policy.py)
   - How to run it with unit tests
    ```shell
    coverage run -m unittest loan_compliance/loan_policy.py
    ```
    ```shell
    coverage report -m
    ```
- [a generator of decisions with respect to the reference Python implementation](loan_compliance/loan_data_generator.py)

## Data
### Schema

#### Input Parameters

| Parameter      | Type         | Description                                                | Allowed Values |
|----------------|--------------|------------------------------------------------------------|----------------|
| `applicant`    | `Applicant`  | The primary individual applying for the loan.              | N/A            |
| `co_signer`    | `Applicant`  | An optional secondary applicant who can support the loan.  | N/A            |
| `loan_amount`  | `float`      | The amount of money requested for the loan.                | N/A            |

##### Applicant Attributes

| Attribute                      | Type    | Description                                                              | Allowed Values                                                                                 |
|--------------------------------|---------|--------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| `birth_date`                   | `date`  | The applicant’s date of birth.                                           | N/A                                                                                            |
| `address`                      | `Dict`  | The applicant’s residential address details.                             | N/A                                                                                            |
| `credit_score`                 | `float` | The applicant’s credit score, which may affect loan approval and terms.  | N/A                                                                                            |
| `annual_income`                | `float` | The total income earned by the applicant per year before taxes.          | N/A                                                                                            |
| `income_document`              | `str`   | The type of document provided to verify income.                          | `"pay_stub", "tax_return", "bank_statement"`                                                   |
| `employment_status`            | `str`   | The applicant’s current employment situation.                            | `"unemployed", "self-employed", "part-time", "full-time", "contractor", "seasonal worker" ...` |
| `is_financial_record_present`  | `bool`  | Indicates if the applicant has provided financial records for review.    | `True` or `False`                                                                              |
| `monthly_debt_amount`          | `float` | The total monthly debt obligations of the applicant.                     | N/A                                                                                            |
| `monthly_gross_income`         | `float` | The total monthly income of the applicant before taxes.                  | N/A                                                                                            |

#### Output Parameters

| Parameter        | Type    | Description                                                                                                |
|------------------|---------|------------------------------------------------------------------------------------------------------------|
| `eligibility`    | `bool`  | Indicates if the applicant meets the loan approval policy requirements.                                    |
| `interest_rate`  | `float` | The assigned interest rate for the loan, based on the applicant’s credit score and financial profile.      |
| `reason`         | `str`   | Explanation of the loan decision. If eligible, the format is `"Loan approved with {interest_rate} APR."`.  |

An example of a decision row of the dataset, cumulating input and output parameters: 
```text
"{""birth_date"": ""2014-03-06"", ""address"": {""country"": ""US""}, ""credit_score"": 623, ""annual_income"": 71766, ""income_document"": ""pay_stub"", ""employment_status"": ""full-time"", ""is_financial_record_present"": true, ""monthly_debt_amount"": 420, ""monthly_gross_income"": 12431}","{""birth_date"": ""1994-03-11"", ""address"": {""country"": ""US""}, ""credit_score"": 687, ""annual_income"": 73430, ""income_document"": ""pay_stub"", ""employment_status"": ""full-time"", ""is_financial_record_present"": true, ""monthly_debt_amount"": 798, ""monthly_gross_income"": 18742}","12003","True","14.54","Loan approved with 14.54% APR."
```

### Datasets
Data provided out of the box and produced by the generator and policy reference implementation:
- [a decision dataset with 100 entries](loan_compliance/loan_policy_test_dataset_100.csv)
- [a decision dataset with 1000 entries](loan_compliance/loan_policy_test_dataset_1K.csv)

You are free to generate more synthetic datasets by running the [decision code generator](loan_compliance/loan_data_generator.py)

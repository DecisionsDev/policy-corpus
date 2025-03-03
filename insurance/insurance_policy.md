# Car insurance compliance and preliminary fee policy 


## Policy
This car insurance compliance and preliminary fee policy outlines the requirements an applicant must meet to qualify for coverage. This policy serves as a general guide and can be adapted based on specific insurer rules and regulations.
[The policy in plain text](basic_eligibility_car_insurance.txt)

## Code
Associated code contains:
- [a reference implementation of the policy in Python](insurance_compliance/insurance_policy.py)
   - How to run it with unit tests
    ```shell
    coverage run -m unittest insurance_compliance/insurance_policy.py
    ```
    ```shell
    coverage report -m
    ```
- [a generator of decisions with respect to the reference Python implementation](insurance_compliance/insurance_data_generator.py)

## Data
### Schema

#### Input Parameters

| Parameter             | Type              | Description                                            | Allowed Values |
|-----------------------|-------------------|--------------------------------------------------------|----------------|
| `applicants`          | `List[Applicant]` | List of individuals applying for insurance.            | N/A            |
| `vehicle`             | `Vehicle`         | The vehicle to be insured.                             | N/A            |
| `liability_coverage`  | `float`           | The coverage amount for liability insurance.           | N/A            |
| `state_min_liability` | `float`           | The minimum liability coverage required by the state.  |  N/A           |

##### Applicant Attributes

| Attribute            | Type              | Description                                                                | Allowed Values |
|----------------------|-------------------|----------------------------------------------------------------------------|----------------|
| `birth_date`         | `date`            | The applicant’s date of birth.                                             | N/A            |
| `driving_license`    | `DrivingLicense`  | The applicant’s driving license details.                                   | N/A            |
| `family_members`     | `List[Applicant]` | List of family members related to the applicant.                           | N/A            |
| `driving_history`    | `List[Dict]`      | A record of the applicant’s past driving incidents, violations, or claims. | N/A            |
| `address`            | `Dict`            | The applicant’s residential address details.                               | N/A            |
| `is_primary_holder`  | `bool`            | Indicates whether the applicant is the primary policyholder.               | N/A            |
| `credit_score`       | `float`           | The applicant’s credit score, which may affect insurance rates.            | N/A            |

##### DrivingLicense Attributes

| Attribute         | Type         | Description                                            | Allowed Values                                       |
|-------------------|--------------|--------------------------------------------------------|------------------------------------------------------|
| `status`          | `str`        | The current status of the driving license.             | `"valid"`, `"invalid"`, `"revoked"`, `"suspended"`   |
| `issue_date`      | `date`       | The date when the license was issued.                  | N/A                                                  |
| `expiration_date` | `date`       | The date when the license will expire.                 | N/A                                                  |
| `status_history`  | `List[Dict]` | A history of changes in the license status over time.  | N/A                                                  |
| `issue_country`   | `str`        | The country where the license was issued.              | N/A                                                  |

##### Vehicle Attributes
| Attribute                   | Type        | Description                                                   | Allowed Values                                               |
|-----------------------------|-------------|---------------------------------------------------------------|--------------------------------------------------------------|
| `registered_on`             | `Applicant` | The applicant under whom the vehicle is registered.           | N/A                                                          |
| `vehicle_use`               | `str`       | The intended usage of the vehicle.                            | `"personal"`, `"commercial"`                                 |
| `passed_safety_inspections` | `bool`      | Indicates whether the vehicle has passed safety inspections.  | N/A                                                          |
| `date_creation`             | `bool`      | The date when the vehicle was added to the system.            | N/A                                                          |
| `vehicle_type`              | `normal`    | The classification of the vehicle.                            | `"normal"`, `"sport"`, `"highperformance"`, `"salvagetitle"` |


#### Output Parameters

| Parameter     | Type    | Description                                                        |
|---------------|---------|--------------------------------------------------------------------|
| `eligible`    | `bool`  | Indicates if the applicants complies with the policy.              |
| `premium_fee` | `float` | The total fee for an insurance coverage.                           |
| `reason`      | `str`   | A reason of coverage refusal. Is None if the applicant is eligible |

An example of a decision row of the dataset, cumulating input and output parameters: 
```text
"[  {    ""birth_date"": ""2006-03-02"",    ""driving_license"": {      ""status"": ""valid"",      ""issue_date"": ""2022-02-26"",      ""expiration_date"": ""2027-02-25"",      ""status_history"": [],      ""issue_country"": ""us""    },    ""family_members"": [],    ""driving_history"": [],    ""history_insurance_coverage"": [      {        ""lapse"": false,        ""fraud"": false,        ""claims"": 1,        ""cancellation_reason"": null      }    ],    ""address"": {      ""country"": ""us"",      ""state"": ""florida""    },    ""is_primary_holder"": true,    ""credit_score"": 590  },  {    ""birth_date"": ""1974-03-10"",    ""driving_license"": {      ""status"": ""valid"",      ""issue_date"": ""2016-02-28"",      ""expiration_date"": ""2021-02-26"",      ""status_history"": [],      ""issue_country"": ""us""    },    ""family_members"": [],    ""driving_history"": [],    ""history_insurance_coverage"": [      {        ""lapse"": false,        ""fraud"": false,        ""claims"": 2,        ""cancellation_reason"": null      }    ],    ""address"": {      ""country"": ""us"",      ""state"": ""california""    },    ""is_primary_holder"": false,    ""credit_score"": 651  },  {    ""birth_date"": ""1983-03-08"",    ""driving_license"": {      ""status"": ""valid"",      ""issue_date"": ""2016-02-28"",      ""expiration_date"": ""2021-02-26"",      ""status_history"": [],      ""issue_country"": ""us""    },    ""family_members"": [],    ""driving_history"": [],    ""history_insurance_coverage"": [      {        ""lapse"": false,        ""fraud"": false,        ""claims"": 1,        ""cancellation_reason"": null      }    ],    ""address"": {      ""country"": ""us"",      ""state"": ""ohio""    },    ""is_primary_holder"": false,    ""credit_score"": 836  }]","{""registered_on"": {""birth_date"": ""2006-03-02"", ""driving_license"": {""status"": ""valid"", ""issue_date"": ""2022-02-26"", ""expiration_date"": ""2027-02-25"", ""status_history"": [], ""issue_country"": ""us""}, ""family_members"": [], ""driving_history"": [], ""history_insurance_coverage"": [{""lapse"": false, ""fraud"": false, ""claims"": 1, ""cancellation_reason"": null}], ""address"": {""country"": ""us"", ""state"": ""florida""}, ""is_primary_holder"": true, ""credit_score"": 590}, ""vehicle_use"": ""personal"", ""passed_safety_inspections"": true, ""date_creation"": ""2015-02-28"", ""vehicle_type"": ""normal""}",146895,50000,True,1300.0,
```

### Datasets
Data provided out of the box and produced by the generator and policy reference implementation:
- [a decision dataset with 100 entries](insurance_compliance/insurance_test_dataset_100.csv)
- [a decision dataset with 1000 entries](insurance_compliance/insurance_test_dataset_1K.csv)

You are free to generate more synthetic datasets by running the [decision code generator](insurance_compliance/insurance_data_generator.py)

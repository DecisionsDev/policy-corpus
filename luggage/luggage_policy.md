# Luggage compliance and pricing policy 


## Policy
This luggage compliance and pricing policy aims to provide clear guidelines to passengers for preparing their baggage when flying with SkyWings Airlines. By adhering to these rules, passengers can ensure a smooth check-in process and contribute to overall flight safety and punctuality.

[The policy in plain text](luggage_policy.txt)

## Code
Associated code contains:
- [a reference implementation of the policy in Python](luggage_compliance/luggage_policy.py)
   - How to run it with unit tests
    ```shell
    coverage run -m unittest luggage_compliance/luggage_policy.py
    ```
    ```shell
    coverage report -m
    ```
- [a generator of decisions with respect to the reference Python implementation](luggage_compliance/luggage_data_generator.py)

## Data
### Schema

#### Input Parameters

| Parameter       | Type          | Description                                                                 | Allowed Values                         |
|-----------------|---------------|-----------------------------------------------------------------------------|---------------------------------------|
| `travel_class`  | `str`         | The travel class of the passenger.                                         | `"Economy"`, `"Business"`, `"First"` |
| `age_category`  | `str`         | The age category of the passenger.                                          | `"adult"`, `"child"`, `"infant"`     |
| `luggages`      | `List[Luggage]` | A list of `Luggage` objects representing the luggage items for the passenger. | N/A                                   |

##### Luggage Attributes

| Attribute       | Type          | Description                                                                 | Allowed Values                         |
|-----------------|---------------|-----------------------------------------------------------------------------|---------------------------------------|
| `storage`       | `str`         | The type of storage for the luggage.                                       | `"carry-on"`, `"checked"`, `"personal"` |
| `excess`        | `bool`        | Indicates if the luggage is excess.                                        | N/A                                   |
| `special`       | `bool`        | Indicates if the luggage is special.                                       | N/A                                   |
| `compliance`    | `bool`        | Indicates if the luggage complies with the policy.                         | N/A                                   |
| `weight`        | `float`       | The weight of the luggage in kilograms.                                    | N/A                                   |
| `dim`           | `dict`        | The dimensions of the luggage.                                              | N/A                                   |

##### Dimensions Attributes

| Attribute       | Type          | Description                                                                 | Allowed Values                         |
|-----------------|---------------|-----------------------------------------------------------------------------|---------------------------------------|
| `height`        | `float`       | The height of the luggage in centimeters.                                   | N/A                                   |
| `width`         | `float`       | The width of the luggage in centimeters.                                    | N/A                                   |
| `depth`         | `float`       | The depth of the luggage in centimeters.                                    | N/A                                   |
| `unit`          | `str`         | The unit of measurement for the dimensions.                                  | `"cm"`                                |

#### Output Parameters

| Parameter          | Type          | Description                                                                 |
|--------------------|---------------|-----------------------------------------------------------------------------|
| `compliance_result` | `bool`        | Indicates if the luggage complies with the policy.                         |
| `compliance_message` | `str`        | A message describing the compliance status.                                 |
| `cargo_items`       | `List[Luggage]` | A list of luggage items that must be shipped as cargo.                     |
| `fees`              | `float`       | The total fees for excess luggage.                                          |

An example of a decision row of the dataset, cumulating input and output parameters: 
```text
Business,adult,"[{""storage"": ""checked"", ""excess"": false, ""special"": false, ""compliance"": true, ""weight"": 43.49, ""height"": 99.88, ""width"": 15.85, ""depth"": 15.52, ""unit"": ""cm""}, {""storage"": ""personal"", ""excess"": true, ""special"": true, ""compliance"": true, ""weight"": 26.64, ""height"": 76.8, ""width"": 39.53, ""depth"": 26.22, ""unit"": ""cm""}, {""storage"": ""checked"", ""excess"": true, ""special"": true, ""compliance"": true, ""weight"": 10.95, ""height"": 3.34, ""width"": 32.69, ""depth"": 29.85, ""unit"": ""cm""}, {""storage"": ""personal"", ""excess"": false, ""special"": true, ""compliance"": true, ""weight"": 30.36, ""height"": 10.56, ""width"": 67.72, ""depth"": 32.57, ""unit"": ""cm""}, {""storage"": ""personal"", ""excess"": true, ""special"": false, ""compliance"": true, ""weight"": 25.82, ""height"": 44.01, ""width"": 64.35, ""depth"": 38.18, ""unit"": ""cm""}]",False,False,Exceeded carry-on weight limit.,,0
```

### Datasets
Data provided out of the box and produced by the generator and policy reference implementation:
- [a decision dataset with 100 entries](luggage_compliance/luggage_policy_test_dataset_100.csv)
- [a decision dataset with 1000 entries](luggage_compliance/luggage_policy_test_dataset_1K.csv)

You are free to generate more synthetic datasets by running the [decision code generator](luggage_compliance/luggage_data_generator.py)

# Luggage compliance and pricing policy 


## Policy
This luggage compliance and pricing policy aims to provide clear guidelines to passengers for preparing their baggage when flying with SkyWings Airlines. By adhering to these rules, passengers can ensure a smooth check-in process and contribute to overall flight safety and punctuality.

[The policy in plain text](luggage_policy.txt)

## Code
Associated code contains:
- [a reference implementation of the policy in Python](luggage_policy.py)
- [a generator of decisions with respect to the reference Python implementation](luggage_policy_decision_generator.py)

## Data
### Schema

| Name | Type  | Values |
|-------|--------|------|
| travel_class | string  | "Economy", "Business", "First" |
| carry_on_items | string capturing in JSON elements  | {'w': theweight, 'dim': [high, width, prof]} |
| personal_items | string capturing in JSON elements  | {'w': theweight, 'dim': [high, width, prof]} |
| checked_items | string capturing in JSON elements  | {'w': theweight, 'dim': [high, width, prof]} |
| passenger_type | string  | "infant", "child", "adult" |

| Name | Type  | Values |
|-------|--------|------|
| compliance | string  | "True"", "False" |
| reason | string | The description of the outcome|
| fees | number | numeric value |

An example of a decision row of the dataset, cumulating input and output parameters: Business,"[{'w': 0, 'dim': [33, 25, 23]}, {'w': 11, 'dim': [44, 34, 17]}]",[],[],adult,True,Checked luggage complies with the policy.,0

### Datasets
Data provided out of the box and produced by the generator and policy reference implementation:
- [a decision dataset with 100 entries](luggage_policy_decisions_100.csv)
- [a decision dataset with 1000 entries](luggage_policy_decisions_1K.csv)
- [a decision dataset with 10000 entries](luggage_policy_decisions_10K.csv)
- [a decision dataset with 100000 entries](luggage_policy_decisions_100K.csv)
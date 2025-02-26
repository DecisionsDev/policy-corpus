# The template for the new Policies testers

```python
import sys
import os

from {compliance_implementation_filename} import {compliance_name}

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_tester import PolicyTester

if __name__ == "__main__":
    config = {
        'policy_class': {compliance_name}, # Example: LuggageCompliance
        'csv_file': {generated_csv_file_path_and_name}, # Example: 'luggage_policy_test_dataset_100.csv',
        # Example:    
        # 'parse_functions': {
        #     'luggages': lambda x: [Luggage.from_dict(item) for item in json.loads(x)],
        #     'cargo_items': lambda x: [Luggage.from_dict(item) for item in json.loads(x)] if pd.notnull(x) else []
        # }
        # (Optional), but if not set -> no statistical evaluation
        'parse_functions': {dictionary_of_parse_functions}, # format: {'{column_name}': {function_call}}
        'eval_columns': [{list_of_columns_names_exactly_as_they_are_returned_with_compliance}], # Example:  ["compliance_result", "compliance_message", "cargo_items", "fees"],
        # (Optional):
        'evaluators': [{list_of_evaluators_functions}] # Example: [cargo_items_evaluator]
    }
    tester = PolicyTester(
        config['policy_class'], 
        config['csv_file'], 
        config.setdefault('parse_functions', None), 
        config.setdefault('eval_columns', None), 
        config.setdefault('evaluators', None)
    )
    tester.run()

```
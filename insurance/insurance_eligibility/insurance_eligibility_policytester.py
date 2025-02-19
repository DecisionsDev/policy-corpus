import sys
import os

from insurance.insurance_eligibility.insurance_eligibility_compliance import CarInsuranceCompliance

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_tester import PolicyTester

if __name__ == "__main__":
    config = {
        'policy_class': CarInsuranceCompliance,
        'csv_file': 'insurance_test_dataset_1K.csv',
        'parse_functions': {},
        'eval_columns': ["eligible", "premium_fee", "error_message"],
    }
    tester = PolicyTester(config['policy_class'], config['csv_file'], config['parse_functions'], config['eval_columns'], config.setdefault('evaluators', None))
    tester.run()

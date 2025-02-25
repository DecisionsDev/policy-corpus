import sys
import os

from insurance.insurance_compliance.insurance_compliance import CarInsuranceCompliance

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_tester import PolicyTester

if __name__ == "__main__":
    config = {
        'policy_class': CarInsuranceCompliance,
        'csv_file': 'insurance_test_dataset_100.csv',
        'eval_columns': ["eligible", "premium_fee", "reason"],
    }
    tester = PolicyTester(
        config['policy_class'],
        config['csv_file'],
        config.setdefault('parse_functions', None),
        config.setdefault('eval_columns', None),
        config.setdefault('evaluators', None)
    )
    tester.run()

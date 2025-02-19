import sys
import os

from loan_compliance import LoanApprovalCompliance

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_tester import PolicyTester

if __name__ == "__main__":
    config = {
        'policy_class': LoanApprovalCompliance,
        'csv_file': 'loan_policy_test_dataset_1K.csv',
        'parse_functions': {},
        'eval_columns': ["eligibility", "interest_rate", "message"],
    }
    tester = PolicyTester(config['policy_class'], config['csv_file'], config['parse_functions'], config['eval_columns'], config.setdefault('evaluators', None))
    tester.run()

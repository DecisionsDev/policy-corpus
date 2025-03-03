import sys
import os

from loan_policy import LoanApprovalPolicy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_tester import PolicyTester

if __name__ == "__main__":
    config = {
        'policy_class': LoanApprovalPolicy,
        'csv_file': 'loan_policy_test_dataset_100.csv',
        'eval_columns': ["eligibility", "interest_rate", "reason"],
        'save_in_csv': False
    }
    tester = PolicyTester(
        config['policy_class'],
        config['csv_file'],
        config.setdefault('parse_functions', None),
        config.setdefault('eval_columns', None),
        config.setdefault('evaluators', None),
        config.setdefault('save_in_csv', False)
    )
    tester.run()

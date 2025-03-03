import sys
import os

from loan_compliance import LoanApprovalPolicy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_tester import PolicyTester

if __name__ == "__main__":
    config = {
        'policy_class': LoanApprovalPolicy,
        'csv_file': 'loan_policy_test_dataset_1K.csv',
        'eval_columns': ["eligibility", "interest_rate", "message"],
    }
    tester = PolicyTester(
        config['policy_class'],
        config['csv_file'],
        config.setdefault('parse_functions', None),
        config.setdefault('eval_columns', None),
        config.setdefault('evaluators', None)
    )
    tester.run()

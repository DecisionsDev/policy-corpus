from loan.basic_loan_approval.basic_loan_approval import LoanApprovalPolicy
from common.common.generic_tester import PolicyTester

if __name__ == "__main__":
    config = {
        'policy_class': LoanApprovalPolicy,
        'csv_file': 'basic_loan_approval_dataset.csv',
        'parse_functions': {}
    }
    tester = PolicyTester(config['policy_class'], config['csv_file'], config['parse_functions'])
    tester.run()

from insurance.insurance_eligibility.insurance_eligibility import InsuranceEligibilityPolicy
from common.common.generic_tester import PolicyTester

if __name__ == "__main__":
    config = {
        'policy_class': InsuranceEligibilityPolicy,
        'csv_file': 'insurance_eligibility_dataset.csv',
        'parse_functions': {}
    }
    tester = PolicyTester(config['policy_class'], config['csv_file'], config['parse_functions'])
    tester.run()

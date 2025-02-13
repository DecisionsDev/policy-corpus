import pprint
import time

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score

from loan.basic_loan_approval.basic_loan_approval import LoanApprovalPolicy


class PolicyTester:
    def __init__(self, policy_class, csv_file, parse_functions):
        self.policy_class = policy_class
        self.csv_file = csv_file
        self.parse_functions = parse_functions
        self.data = None
        self.policy = None

    def load_data(self):
        self.data = pd.read_csv(self.csv_file)
        for column, parse_function in self.parse_functions.items():
            if column == '*c':
                for df_column in self.data.columns:
                    self.data.rename(columns={f'{df_column}': parse_function(df_column)}, inplace=True)
            else:
                self.data[column] = self.data[column].apply(parse_function)

    def initialize_policy(self):
        self.policy = self.policy_class()

    def test_policy(self):
        results = []
        messages = []
        execution_times = []

        for index, row in self.data.iterrows():
            start_time = time.time()
            result, message = self.policy.test_eligibility(row)
            execution_time = time.time() - start_time

            results.append(result)
            messages.append(message)
            execution_times.append(execution_time)

        return results, messages, execution_times

    def calculate_metrics(self, y_true, y_pred):
        accuracy = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        return accuracy, f1, recall, precision

    def run(self):
        self.load_data()
        self.initialize_policy()
        results, messages, execution_times = self.test_policy()

        y_true = self.data['eligibility']
        y_pred = results

        accuracy, f1, recall, precision = self.calculate_metrics(y_true, y_pred)
        average_execution_time = np.array(execution_times).mean()

        print(f"Accuracy: {accuracy}")
        print(f"F1 Score: {f1}")
        print(f"Recall: {recall}")
        print(f"Precision: {precision}")
        print(f"Average Execution Time: {average_execution_time} seconds")

        diff_indices = np.where(y_true != y_pred)[0]
        for el in diff_indices:
            print("Case:\n----------")
            pprint.pprint(self.data.loc[el])
            print("---------\n")
            print(f"True value: {y_true[el]}\nPredicted: {y_pred[el]}, Message: {messages[el]}")
            print("=========\n")


if __name__ == "__main__":
    # luggage_config = {
    #     'policy_class': LuggagePolicy,
    #     'csv_file': '../luggage/luggage_compliance/luggage-compliance-pricing-requests-dataset.csv',
    #     'parse_functions': {
    #         'carry_on_items': parse_carry_on_items,
    #         'personal_items': parse_carry_on_items,
    #         'checked_items': parse_items
    #     }
    # }
    #
    # # Run the policy tester with the desired configuration
    # config = luggage_config  # Change to loan_config to test loan approval policy
    # tester = PolicyTester(config['policy_class'], config['csv_file'], config['parse_functions'])
    # tester.run()

    loan_config = {
        'policy_class': LoanApprovalPolicy,
        'csv_file': '../loan/basic_loan_approval/basic_loan_approval_dataset.csv',
        'parse_functions': {}
    }

    # Run the policy tester with the desired configuration
    config = loan_config  # Change to loan_config to test loan approval policy
    tester = PolicyTester(config['policy_class'], config['csv_file'], config['parse_functions'])
    tester.run()

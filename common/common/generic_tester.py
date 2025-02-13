import pprint
import time

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score

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
        parameters = []
        execution_times = []

        for index, row in self.data.iterrows():
            start_time = time.time()
            result = self.policy.test_eligibility(row)
            execution_time = time.time() - start_time

            results.append(result[0])
            parameters.append(result)
            execution_times.append(execution_time)

        return results, parameters, execution_times

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

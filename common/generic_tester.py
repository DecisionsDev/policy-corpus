import pprint
import time
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
from sklearn.preprocessing import LabelEncoder


class PolicyTester:
    def __init__(self, policy_class, csv_file, parse_functions=None, eval_columns=None, evaluators=None):
        """
        :param policy_class: The policy class to be tested.
        :param csv_file: Path to the CSV file.
        :param parse_functions: Dictionary of column-specific parsing functions.
        :param eval_columns: Ordered list of column names expected from test_policy results.
        :param evaluators: List of evaluator functions.
        """
        self.policy_class = policy_class
        self.csv_file = csv_file
        self.parse_functions = parse_functions
        self.evaluators = evaluators
        self.eval_columns = eval_columns
        self.data = None
        self.policy = None

    def load_data(self):
        self.data = pd.read_csv(self.csv_file, na_filter=True).fillna("")
        if not self.parse_functions:
            return
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
        execution_times = []

        for _, row in self.data.iterrows():
            start_time = time.time()
            result = self.policy.test_eligibility(row)
            execution_time = time.time() - start_time

            results.append(result)
            execution_times.append(execution_time)

        return results, execution_times

    @staticmethod
    def calculate_metrics(y_true_encoded, y_pred_encoded):
        # Compute metrics
        accuracy = accuracy_score(y_true_encoded, y_pred_encoded)
        f1 = f1_score(y_true_encoded, y_pred_encoded, average="weighted", zero_division=0.0)
        recall = recall_score(y_true_encoded, y_pred_encoded, average="weighted", zero_division=0.0)
        precision = precision_score(y_true_encoded, y_pred_encoded, average="weighted", zero_division=0.0)

        print(f"  Accuracy: {accuracy}")
        print(f"  F1 Score: {f1}")
        print(f"  Recall: {recall}")
        print(f"  Precision: {precision}")

        return {"accuracy": accuracy, "f1": f1, "recall": recall, "precision": precision}


    def statistics_tester(self, results_transposed):
        diff_indices = {}
        label_encoder = LabelEncoder()

        metrics = {}

        for idx, column in enumerate(self.eval_columns):
            y_true = self.data[column]
            y_pred = results_transposed[idx] if idx < len(results_transposed) else []

            if len(y_pred) != len(y_true):
                print(f"Skipping evaluation for {column} due to size mismatch.")
                continue

            # Boolean and numerical columns can be directly compared
            if y_true.dtype == bool or np.issubdtype(y_true.dtype, np.number):
                y_true_encoded = y_true.astype(int)  # Convert bool to int if needed
                y_pred_encoded = np.array(y_pred, dtype=int)
            else:
                # Assume string values, arrays, dictionaries, apply LabelEncoder
                y_true = y_true.astype(str)
                y_pred = [str(pred) for pred in y_pred]

                label_encoder.fit(list(y_true) + y_pred)
                y_true_encoded = label_encoder.transform(y_true)
                y_pred_encoded = label_encoder.transform(y_pred)

            print(f"\nMetrics for {column}:")
            metrics[column] = self.calculate_metrics(y_true_encoded, y_pred_encoded)

            diff_indices[column] = np.where(y_true_encoded != y_pred_encoded)[0]

        return metrics, diff_indices

    def run(self):
        self.load_data()
        self.initialize_policy()
        test_results, execution_times = self.test_policy()

        # Transpose results to match columns
        results_transposed = list(zip(*test_results))
        average_execution_time = np.mean(execution_times)
        if self.evaluators:
            print("Evaluation Results:")
            for evaluator in self.evaluators:
                evaluator(self.data, results_transposed)

            print(f"\nAverage Execution Time: {average_execution_time} seconds")

        if not self.eval_columns:
            print("The eval_columns are not specified! Skipping...")
            return

        metrics, diff_indices = self.statistics_tester(results_transposed)

        for column, indices in diff_indices.items():
            for el in indices:
                print(f"\nDiscrepancy in {column}:")
                print("Case:")
                pprint.pprint(self.data.loc[el])
                print(
                    f"True value: {self.data[column][el]},\nPredicted: {results_transposed[self.eval_columns.index(column)][el]}")
                print("=========")

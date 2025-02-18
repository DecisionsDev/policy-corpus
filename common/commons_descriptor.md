# Common elements description
## generic_tester.py

The ``PolicyTester`` class inside is designed to evaluate the performance of a policy implementation by testing its eligibility function on a dataset loaded from a CSV file. The class supports custom parsing of input data, execution time measurement, and statistical evaluation of policy results.

---

### Class: PolicyTester

#### Constructor
```python
def __init__(self, policy_class, csv_file, parse_functions, eval_columns=None, evaluators=None)
```

**Parameters**:
* ``policy_class`` (class): The class implementing the policy to be tested. It should have a method test_eligibility(row), which processes a single data row and returns a result.
* ``csv_file`` (str): Path to the CSV file containing test cases.
* ``parse_functions`` (dict): A dictionary where keys are column names and values are functions to parse and preprocess column data.
* ``eval_columns`` (list, optional): A list of column names expected in the policy results, used for evaluation.
* ``evaluators`` (list, optional): A list of custom evaluation functions that take in the dataset and test results.

**Attributes**:
* ``self.data`` (DataFrame): Stores the loaded test data.
* ``self.policy`` (object): An instance of the provided policy class.

### Methods

```python
def load_data(self)
```
Loads test data from the CSV file and applies parsing functions. Supports wildcard parsing ('*c') to apply a function to all columns.

---

```python
def initialize_policy(self)
```
Initializes an instance of the provided policy class.

---

```python
def test_policy(self)
```

Executes the test_eligibility method of the policy on each row of the dataset, recording execution time.

**Returns**:
* results (list of lists): The predicted outputs for each test case.
* execution_times (list of floats): Execution times for each test case.

---

```python
@staticmethod
def calculate_metrics(y_true_encoded, y_pred_encoded)
```

Computes **standard classification metrics**:

* **Accuracy**: Measures the percentage of correct predictions.
* **F1 Score**: Balances precision and recall, particularly useful for imbalanced data.
* **Recall**: Measures the proportion of actual positives correctly identified.
* **Precision**: Measures the proportion of predicted positives that are actually correct.

These metrics are selected because they provide a broad evaluation of classifier performance, balancing correctness and misclassification rates.

The ``weighted`` Averaging Methods is selected. The Comparison of Different Averaging Methods in Sklearn is given here:

**Comparison of Different Averaging Methods in Sklearn**

| Averaging Method | How It Works                                                                                  | Best Used For                                                                     | Handles Class Imbalance?                                                                               |
|:-----------------|:----------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------|
| micro            | Computes global TP, FP, FN across all classes before calculating the metric                   | Good for imbalanced datasets when you care about total classification performance | ✅ Yes (by counting all instances equally)                                                              |
| macro            | Calculates metrics for each class separately, then averages them (treats all classes equally) | Good for balanced datasets                                                        | ❌ No (small classes contribute equally to large ones)                                                  |
| weighted         | Calculates metrics per class, then weights by class support (number of samples in each class) | Best for imbalanced datasets                                                      | ✅ Yes (gives more importance to larger classes)                                                        |
| samples          | Computes metrics for each sample separately (used for multi-label classification)             | Only for multi-label classification (e.g., tagging, image labeling)               | ❌ No                                                                                                   | 

---

```python
def statistics_tester(self, results_transposed)
```
Compares predicted outputs (``y_pred``) with ground truth (``y_true``) for each evaluation column. Uses ``LabelEncoder`` for categorical data.

**Handling of Data Types:**
* Boolean/Numeric Columns: Directly compared after converting to integers.
* String/JSON Columns: Encoded using ``LabelEncoder`` for comparison.

**🚨 Limitations for JSON-Based Classes**

* Standard statistical metrics (``accuracy``, ``F1-score``, etc.) do not fully reflect correctness for structured data (like JSON or object lists).
* JSON-based predictions may have minor format mismatches (e.g., reordered keys, whitespace differences), which could lead to false negatives in metric calculations.

Instead, object-based equality checks (__eq__) should be implemented in the corresponding classes to compare structured data more accurately and another method to parse the rows of data to the corresponding classes and their further comparison must be implemented and passed to the method with ``evaluators``. Example: [luggage_compliance_policy_tester.py](../luggage/luggage_compliance/luggage_compliance_policy_tester.py)

**Returns**:
* ``metrics`` (dict): Dictionary with metric results per evaluation column.
* ``diff_indices`` (dict): Lists of indices where predictions differ from true values.

---

```python
def run(self)
```
Orchestrates the entire testing process:

1. Loads and preprocesses data.
2. Initializes the policy class.
3. Runs ``test_policy()``.
4. Calls custom evaluators (if any).
5. Computes statistics and detects discrepancies.

**Handles**:
* Execution time measurement.
* Column-wise metric evaluation.
* Debugging output for incorrect predictions.

**🚨 Limitations for JSON-Based Data**:

The ``eval_columns`` parameter must contain exact sequence of the column names, as they are returned by the policy's ``test`` method. Thus means, if ``test`` method returns: ``({eligibility}, {messages}, {fee})``, then the ``eval_columns`` must be: ``['eligibility', 'messages', 'fee']``.


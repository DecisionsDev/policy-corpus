# Common elements description
## [abstract_policy.py](abstract_policy.py)

The ``Policy`` class is an abstract base class (ABC) designed to define a policy framework. It serves as a template for implementing various policies that assess eligibility, or any other automation logic, based on predefined criteria. 

---

### Abstract methods (to be implemented)

```python
def test_eligibility(self, case) -> Tuple:
```

This abstract method must be implemented by any subclass. It determines whether an applicant meets the eligibility criteria defined by the specific policy.

**Parameters**:
* ``case`` (dict or a related policy class instance): The input data containing the necessary information to evaluate eligibility.

**Returns**: A tuple, which allows to determine if the outcome of the test is positive and negative.

### Implementation Requirements

1. **Subclassing**: Any subclass must inherit from ``Policy`` and implement the ``test_eligibility`` method.
2. **Unit Testing**: Implement meaningful unit tests covering various cases described in the policy document.

## [generic_data_generator.py](generic_data_generator.py)

The ``DataGenerator`` class is an abstract base class (ABC) designed for generating test datasets for policy evaluation. It provides a structured approach to generating eligible and non-eligible test cases and ensures that child classes define key column names and case-generation methods.

---

### Abstract Properties

Abstract properties that must be implemented by subclasses.

```python
COLUMN_NAMES (List[str])
```
A property to define the dataset's column names.

```python
EVAL_COLUMN_NAMES (List[str])
```

A property to specify the column names expected in policy evaluation results.

### Constructor
```python
def __init__(self, policy_checker: Policy):
```
**Parameters**:

* ``policy_checker (Policy)``: An instance of a policy class used to determine eligibility.

### Methods

```python
def generate_test_dataset(self, num_samples=100) -> pd.DataFrame
```

Generates a test dataset with approximately equal numbers of positive and negative cases.

**Parameters**:
* ``num_samples (int)``: The total number of test cases to generate.

**Returns**:
* A ``pandas.DataFrame`` containing the generated test cases.

```python 
def determine_eligibility(self, row) -> Tuple
```

Uses the ``policy_checker`` instance to determine the eligibility of a given row.

**Parameter**:

* ``row (dict)``: A single test case from the dataset.

**Returns**:
* A tuple containing the eligibility result and relevant details.

```python
def get_constant(self) -> Dict
```

Collects and returns a dictionary of all uppercase-defined constants in the class.

**Returns**:
* A dictionary where keys are constant names and values are their assigned values.

### Utility Function
```python
def format_data_units(n) -> str
```

Formats a numeric value into a human-readable string with units (K for thousands, M for millions).

**Parameter**:
* ``n (int)``: The numeric value to format.

**Returns**:
* A formatted string representing the number with an appropriate unit suffix.

### Abstract methods (to be implemented)
```python
def generate_eligible_case(self) -> Dict
```
Must be implemented to generate an individual test case that is eligible.

**Returns**:
* A dictionary representing an eligible test case.

```python
def generate_non_eligible_case(self) -> Dict
```
Must be implemented to generate an individual test case that is not eligible.

**Returns**:
* A dictionary representing a non-eligible test case.

## [generic_tester.py](generic_tester.py)

The ``PolicyTester`` class inside is designed to evaluate the performance of a policy implementation by testing its eligibility function on a dataset loaded from a CSV file. The class supports custom parsing of input data, execution time measurement, and statistical evaluation of policy results.

---

### Constructor
```python
def __init__(self, policy_class, csv_file, parse_functions=None, eval_columns=None, evaluators=None, save_in_csv=False)
```

**Parameters**:
* ``policy_class`` (class): The class implementing the policy to be tested. It should have a method test_eligibility(row), which processes a single data row and returns a result.
* ``csv_file`` (str): Path to the CSV file containing test cases.
* ``parse_functions`` (dict, optional): A dictionary where keys are column names and values are functions to parse and preprocess column data.
* ``eval_columns`` (list, optional): A list of column names expected in the policy results, used for evaluation.
* ``evaluators`` (list, optional): A list of custom evaluation functions that take in the dataset and test results.
* ``save_in_csv`` (bool, optional): Mark if the testing results are saved in a ``ROOT_DIR/output`` or not. Set to True to save the testing predicted results, metrics and different samples.
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


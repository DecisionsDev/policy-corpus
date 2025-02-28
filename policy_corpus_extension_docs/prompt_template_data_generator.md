**Prompt**:

I need you to inherit and implement a Python class by **strictly adhering** to a given abstract class structure and ensuring that the generated data aligns with the provided compliance checker.

The generated test data should **fully respect** the eligibility logic implemented in the policy_checker while following the structure of the DataGenerator abstract class. It must contain **tricky samples**, covering **all** the cases described in automatic policy.

Additionally, the implementation must call the super ``determine_eligibility`` method and store its results correctly in the dataset.

* Below is the abstract class that defines the structure:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.abstract_policy import Policy


class DataGenerator(ABC):

    ################# CONSTANT PROPERTIES #################
    @property
    @abstractmethod
    def COLUMN_NAMES(self) -> List[str]:
        """
        Abstract property to enforce the definition of column names in child classes.
        """
        pass

    @property
    @abstractmethod
    def EVAL_COLUMN_NAMES(self) -> List[str]:
        """
        Abstract property to enforce the definition of column names expected in the policy results, used for evaluation.
        """
        pass

    ## PUT ALL OTHER CONSTANTS/ENUMS USED IN THE CODE HERE

    def __init__(self, policy_checker: Policy):
        """
        Initializes the DataGenerator with a policy checker instance.

        :param policy_checker: An instance of a Policy class used for automatic checking.
        """
        self.policy_checker = policy_checker  # Policy instance

    def generate_test_dataset(self, num_samples=100) -> pd.DataFrame:
        """
        Generate a test dataset with an approximately equal number of positive and negative cases.

        :param num_samples: Total number of samples to generate.
        :return: DataFrame containing the generated dataset.
        """
        num_positive = num_samples // 2
        num_negative = num_samples - num_positive  # To handle odd numbers properly

        data = []

        # Generate positive (eligible) cases
        for _ in range(num_positive):
            data.append(self.generate_eligible_case())

        # Generate negative (non-eligible) cases
        for _ in range(num_negative):
            data.append(self.generate_non_eligible_case())

        return pd.DataFrame(data)

    @abstractmethod
    def generate_eligible_case(self) -> Dict:
        """
        Generate an individual test case that is eligible.
        :return: Dictionary representing an eligible test case.
        """
        pass

    @abstractmethod
    def generate_non_eligible_case(self) -> Dict:
        """
        Generate an individual test case that is NOT eligible.
        :return: Dictionary representing a non-eligible test case.
        """
        pass

    def determine_eligibility(self, row) -> Tuple:
        """
        Determine the eligibility of a given row using the policy checker.

        :param row: A row from the dataset.
        :return: The result of the policy checker.
        """
        return self.policy_checker.test_eligibility(row)

    def get_constant(self) -> Dict:
        """
        Return a dictionary of constants defined in this class.

        :return: Dictionary containing class constants.
        """
        constants = {}
        for attr_name in dir(self):
            if attr_name.isupper():  # Check if attribute name is in uppercase
                attr = getattr(self.__class__, attr_name)
                if not callable(attr):
                    constants[attr_name] = attr
        return constants


# For file naming + number samples formatting
def format_data_units(n):
    nb_units = round(n / 1000000)
    if nb_units >= 1:
        unit = "M"
    else:
        nb_units = round(n / 1000)
        if nb_units >= 1:
            unit = "K"
        else:
            nb_units = n
            unit = ""

    label = f'{nb_units}{unit}'
    return label

```

* Policy Checker (Policy subclass): This defines how eligibility is determined and should be used to guide test data generation:

```python
{policy_class_without_unittests}
```

* Here is the policy description document outlining the implementation details:
```text
{policy_document}
```

**Requirements:**

1. Strict Structure Policy:
   * The implementation must follow the DataGenerator abstract class precisely.
   * Do not modify method signatures or inheritance.
   * Implement the abstract properties COLUMN_NAMES and EVAL_COLUMN_NAMES correctly.
2. Generate Data Consistently with the Policy Checker:
   * Implement generate_eligible_case to create cases that pass policy_checker.test_eligibility().
   * Implement generate_non_eligible_case to create cases that fail.
   * Ensure the generated dataset has a balanced distribution (50% eligible, 50% non-eligible).
3. Use the Policy Checker as Context:
    * The policy_checker implementation should directly inform how test cases are structured.
    * If any conflicts or ambiguities arise, prioritize the logic of the policy checker.
4. Call ``determine_eligibility`` and Store Results Correctly:
   * The method ``determine_eligibility(row)`` must be called on each generated data sample.
   * Store the results exactly as returned by ``determine_eligibility``, ensuring they match the expected structure from test_eligibility.
   * The dataset should include:
     * The original data sample (formatted as required by the policy checker).
     * The attributes from the sample.
     * The results returned by determine_eligibility, using the same column names as in ``test_eligibility``.
5. Import Instead of Redefining provided Class:
   * Do not repeat the provided abstract DataGenerator class and functions in it.
   * Instead, import it at the beginning of the implementation:
```python
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.generic_data_generator import DataGenerator
```

  * Do not repeat the provided Policy class.
  * Instead, import it at the beginning of the implementation:
```python
from {file_name} import {policy_name}
```

## Now, please generate the full implementation of the DataGenerator subclass based on these instructions.
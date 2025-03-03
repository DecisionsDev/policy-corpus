**Prompt**:

I need you to inherit and implement a Python class by strictly adhering to a given abstract class structure and incorporating all details from a policy description document.

Additionally, you must provide unit tests that comprehensively cover the cases described in the policy document.

* Below is the abstract class that defines the structure:
```python
from abc import ABC, abstractmethod
from typing import Tuple


class Policy(ABC):
    """
    Abstract base class for defining a policy.

    This class provides a template for implementing various policies that need to test eligibility
    based on certain criteria. Any subclass must implement the `test_eligibility` method
    and cover the newly generated policy with meaningful unittests.
    """

    @abstractmethod
    def test_eligibility(self, case) -> Tuple:
        """
        Abstract method to test the eligibility of an applicant based on the provided information.

        Args:
            case (dict | (preferably) related to the policy class): A super class, containing the row information.

        Returns: Tuple: A tuple, which allows to determine if the outcome of the test is positive and negative.
        Elements of the tuple are external parameters, returned with the result (eligibility, fee, error message, etc).
        """
        pass

#    Testing class, which implements unittest.TestCase
#    and covers as much meaningful cases described in the text policy  document,
#    as possible

```

* Here are the defined data structures, which you need to use in ``test_eligibility`` method:
```python
{predefined_data_structures}
```
If you use these data structures, make sure to add a check and to convert the ``case`` parameter from dictionary to the class instance.

* Here is the policy description document outlining the implementation details:
```text
{policy_document}
```

**Strict Requirements**:
1. Strict Structure Policy:
   * You must implement the ``test_eligibility`` method exactly as defined in the abstract class.
   * Do not modify method signatures or class inheritance.
   * Follow the comments within the abstract class precisely.
2. Complete Policy Coverage:
    * Your implementation should fully cover all cases, rules, and logic described in the policy document.
    * Ensure that no details are omitted from the policy description.
3. Unit Tests (MANDATORY):
   * You must generate a ``unittest.TestCase`` class that thoroughly tests the implemented policy.
   * Unit tests should cover as many meaningful cases from the policy document as possible, ensuring full validation.
   * Ensure edge cases, normal cases, and failure cases are tested.
4. Import Instead of Redefining Abstract Class:
   * Do not repeat the provided abstract Policy class.
   * Instead, import it at the beginning of the implementation:

```python
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.abstract_policy import Policy
```
5. Pythonic & Readable Code:
   * The implementation must follow Pythonic best practices.
   * Use clear variable names, docstrings, and structured error handling.

## Now, please generate:
* The full implementation of the policy class based on the provided abstract class and policy document.
* A complete unittest class that thoroughly tests the policy class.

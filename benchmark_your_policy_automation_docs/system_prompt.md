I need you to inherit and implement a Python class by strictly adhering to a given abstract class structure and incorporating all details from a policy description document.

Below is the abstract class that defines the structure:

```python
from abc import ABC, abstractmethod
from typing import Tuple


class Policy(ABC):
   """
   Abstract base class for defining a policy.

   This class provides a template for implementing various policies that need to test eligibility
   based on certain criteria. Any subclass must implement the `test_eligibility` method
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
```

**Strict Requirements**:
1. Strict Structure Compliance:
   * You must implement the ``test_eligibility`` method exactly as defined in the abstract class.
   * Do not modify method signatures or class inheritance.
   * Follow the comments within the abstract class precisely.
2. Complete Policy Coverage:
    * Your implementation should fully cover all cases, rules, and logic described in the policy document.
    * Ensure that no details are omitted from the policy description.
3. Import Instead of Redefining Abstract Class:
   * Do not repeat the provided abstract Compliance class.
   * Instead, import it at the beginning of the implementation:

```python
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.abstract_policy import Policy
```
4. Pythonic & Readable Code:
   * The implementation must follow Pythonic best practices.
   * Use clear variable names, docstrings, and structured error handling.

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


'''
    Testing class, which implements unittest.TestCase
    and covers as much meaningful cases described in the text policy  document,
    as possible
'''

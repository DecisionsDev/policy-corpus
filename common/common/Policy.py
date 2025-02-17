from abc import ABC, abstractmethod
from typing import Tuple


class Policy(ABC):
    """
    Abstract base class for defining a policy.

    This class provides a template for implementing various policies that need to test eligibility
    based on certain criteria. Any subclass must implement the `test_eligibility` method.
    """

    @abstractmethod
    def test_eligibility(self, info) -> Tuple[bool, ...]:
        """
        Abstract method to test the eligibility of an applicant based on the provided information.

        Args:
            info (dict): A super class, containing the row information.

        Returns: Tuple[bool, ...]: A tuple where the first element is a boolean indicating eligibility, and other
        elements are external parameters, returned with the result (fee, error message, etc).
        """
        pass

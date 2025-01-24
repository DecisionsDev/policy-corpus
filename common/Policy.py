from abc import ABC, abstractmethod
from typing import Tuple


class Policy(ABC):
    """
    Abstract base class for defining a policy.

    This class provides a template for implementing various policies that need to test eligibility
    based on certain criteria. Any subclass must implement the `test_eligibility` method.
    """

    @abstractmethod
    def test_eligibility(self, info) -> Tuple[bool, int]:
        """
        Abstract method to test the eligibility of an applicant based on the provided information.

        Args:
            info (dict): A dictionary containing the applicant's information.

        Returns:
            Tuple[bool, int]: A tuple where the first element is a boolean indicating eligibility,
                              and the second element is an integer code or message explaining the result.
        """
        pass

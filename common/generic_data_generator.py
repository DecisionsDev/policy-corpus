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
        Initializes the DataGenerator with a Policy checker instance.

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

from abc import ABC, abstractmethod
from typing import List, Dict

import pandas as pd


class DataGenerator(ABC):
    @property
    @abstractmethod
    def COLUMN_NAMES(self) -> List[str]:
        """
        Abstract property to enforce the definition of column names in child classes.
        """
        pass

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if 'eligibility' not in cls.COLUMN_NAMES:
            raise ValueError('The column "eligibility" must be included in COLUMN_NAMES.')

    @abstractmethod
    def generate_test_dataset(self, num_samples=100) -> pd.DataFrame:
        """
        Generate a test dataset with the specified number of samples.

        :param num_samples: Number of samples to generate.
        :return: DataFrame containing the generated dataset.
        """
        pass

    @abstractmethod
    def determine_eligibility(self, row) -> bool:
        """
        Determine if a given row is suitable for the case.

        :param row: A row from the dataset.
        :return: Boolean indicating eligibility.
        """
        pass

    def get_constant(self) -> Dict:
        """
        Return the dictionary of constants defined in this class.

        :return: Dictionary of constants.
        """
        constants = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, property) and attr.fget is None:
                constants[attr_name] = attr
        return constants

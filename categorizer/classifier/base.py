import abc
from typing import List, Mapping


class IClassifier(abc.ABC):
    @abc.abstractmethod
    def classify(self, text: str, categories: List[str]) -> Mapping[str, float]:
        """
        Returns probability for each category
        """

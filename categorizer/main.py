from typing import List

import pandas as pd

from categorizer.classifier import IClassifier


class Categorizer:
    def __init__(self, classifier: IClassifier):
        self.classifier = classifier

    def _categorize_text(self, text: str, categories: List[str]) -> str:
        """
        Returns the most suitable category
        """
        prediction = self.classifier.classify(text.lower(), categories)
        category = max(prediction, key=lambda x: prediction[x])
        return category, prediction[category]

    def categorize(
        self, data: pd.DataFrame, categories: List[str], threshold: float = 0.0
    ) -> pd.DataFrame:
        pd.options.mode.chained_assignment = None
        data['category'], data['prob'] = zip(
            *data.text.apply(lambda text: self._categorize_text(text, categories))
        )
        data = data[data.prob > threshold]
        return (
            data.sort_values('prob', ascending=False)
            .reset_index()
            .drop(columns=['index', 'prob'])
        )

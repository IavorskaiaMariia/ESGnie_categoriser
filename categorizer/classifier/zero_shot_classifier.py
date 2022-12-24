from typing import List, Mapping

from transformers import pipeline

from categorizer.classifier import IClassifier


class ZeroShotClassifier(IClassifier):
    def __init__(self):
        self.classifier = pipeline(
            'zero-shot-classification', model='facebook/bart-large-mnli'
        )

    def classify(self, text: str, categories: List[str]) -> Mapping[str, float]:
        """
        Returns probability for each category
        """
        results = self.classifier(text, categories)
        return dict(zip(results['labels'], results['scores']))

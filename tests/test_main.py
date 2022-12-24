from unittest import mock

import pandas as pd
import pytest

from categorizer.classifier import IClassifier
from categorizer.main import Categorizer


@pytest.fixture()
def classifier():
    return mock.create_autospec(IClassifier)


@pytest.mark.parametrize(
    'categories, expected_category',
    [
        ({'category 1': 0.2}, 'category 1'),
        ({'category 1': 0.2, 'category 2': 0.1}, 'category 1'),
        ({'category 1': 0.2, 'category 2': 0.1, 'category 3': 0.3}, 'category 3'),
    ],
)
def test_categorizer(categories, expected_category, classifier):
    classifier.classify.return_value = categories
    categorizer = Categorizer(classifier)
    data = pd.DataFrame({'text': ['text']})
    results = categorizer.categorize(data, list(categories.keys()))

    assert results.iloc[0].category == expected_category


@pytest.mark.parametrize(
    'threshold, expected_data_len',
    [
        (0.1, 1),
        (0.19, 1),
        (0.2, 0),
        (0.3, 0),
    ],
)
def test_categorizer_threshold(threshold, expected_data_len, classifier):
    classifier.classify.return_value = {'category 1': 0.2}
    categorizer = Categorizer(classifier)
    data = pd.DataFrame({'text': ['text']})
    results = categorizer.categorize(data, ['category 1'], threshold)

    assert len(results) == expected_data_len

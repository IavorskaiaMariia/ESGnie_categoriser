import re
from typing import List, Mapping

import pandas as pd
from lazy import lazy

from data import load_texts


def text_contains_words(text: str) -> bool:
    if re.search(r'[a-z]{2}', text.lower()):
        return True
    return False


def clean_text(text: str) -> str:
    text = re.sub(r'[^a-z]', ' ', text.lower())
    return re.sub(r'\s+', ' ', text).strip()


class Storage:
    def __init__(self):
        self._data = load_texts()

    @lazy
    def _clean_data(self) -> pd.DataFrame:
        documents = self._data[~self._data.text.isna()]
        documents = documents[documents.text.apply(len) > 4]
        documents = documents[documents.text.apply(text_contains_words)]
        documents = documents[~documents.text.str.isupper()]

        documents['clean_text'] = documents.text.apply(clean_text)
        documents = documents[
            documents.clean_text.apply(lambda text: len(text.split())) != 1
        ]

        vc_report_texts = documents[
            documents.clean_text.str.contains('report')
        ].clean_text.value_counts()
        report_names = vc_report_texts[vc_report_texts > 2].index.tolist()
        documents = documents[~documents.clean_text.isin(report_names)]

        return documents.reset_index().drop(columns=['clean_text', 'index'])

    @lazy
    def document_names_mapping(self) -> Mapping[str, str]:
        return {
            doc_name: self._data[
                (self._data.doc_name == doc_name) & (self._data.pagenum == 1)
            ].text.values[0]
            for doc_name in self._data.doc_name.unique()
        }

    @lazy
    def columns(self) -> List[str]:
        return self._data.columns.tolist()

    def get_data(self, document_names: List[str]) -> pd.DataFrame:
        pd.options.mode.chained_assignment = None
        data = self._clean_data[self._clean_data.doc_name.isin(document_names)]
        data['doc_name'] = data.doc_name.apply(
            lambda doc_name: self.document_names_mapping[doc_name]
        )
        return data

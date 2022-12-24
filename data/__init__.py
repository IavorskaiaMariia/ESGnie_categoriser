from pathlib import Path

import pandas as pd

data_dir = Path(__file__).resolve().parent


def load_categories():
    return pd.read_csv(data_dir / 'taxonomy.csv')


def load_texts():
    return pd.read_csv(data_dir / 'text_segments.csv')

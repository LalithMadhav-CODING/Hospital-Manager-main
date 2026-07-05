import pandas as pd


def normalize(series: pd.Series) -> pd.Series:
    """
    Min-Max normalization.
    """

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return series * 0

    return (series - minimum) / (maximum - minimum)


def safe_divide(a, b):
    """
    Prevent divide-by-zero.
    """

    if b == 0:
        return 0

    return a / b
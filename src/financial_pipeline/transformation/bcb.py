from datetime import date

import pandas as pd


def filter_bcb_series_period(dataframe: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
    """
    Mantém somente observações dentro do período solicitado.
    """

    if start_date > end_date:
        raise ValueError("start_date não pode ser maior que end_date")

    observation_dates = pd.to_datetime(dataframe["observation_date"]).dt.date

    period_mask = ((observation_dates >= start_date) & (observation_dates <= end_date))

    return dataframe.loc[period_mask].copy().reset_index(drop=True)
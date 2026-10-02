from datetime import date

import pandas as pd
import pytest

from financial_pipeline.ingestion.bcb import extract_bcb_series, normalize_bcb_series


def test_normalize_bcb_series() -> None:
    records = [
        {"data": "02/01/2025", "valor": "12.25"},
        {"data": "01/01/2025", "valor": "12.25"},
        {"data": "01/01/2025", "valor": "12.25"},
    ]

    dataframe = normalize_bcb_series(records=records,series_id=432)

    assert list(dataframe.columns) == [
        "series_id",
        "observation_date",
        "value",
    ]

    assert len(dataframe) == 2
    assert dataframe["series_id"].tolist() == [432, 432]
    assert dataframe["value"].tolist() == [12.25, 12.25]

    assert dataframe["observation_date"].is_monotonic_increasing

    assert pd.api.types.is_datetime64_any_dtype(
        dataframe["observation_date"]
    )


def test_normalize_bcb_series_with_missing_columns() -> None:
    records = [
        {"data": "01/01/2025"}
    ]

    with pytest.raises(ValueError, match="não contém as colunas data e valor",):
        normalize_bcb_series(records=records,series_id=432)


def test_extract_bcb_series_with_invalid_period() -> None:
    with pytest.raises(ValueError, match="start_date não pode ser maior que end_date",):
        extract_bcb_series(
            series_id=432,
            start_date=date(2025, 1, 10),
            end_date=date(2025, 1, 1),
        )
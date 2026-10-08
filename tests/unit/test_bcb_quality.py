from datetime import date

import pandas as pd
import pytest

from financial_pipeline.quality.bcb import  DataQualityError, validate_bcb_series


def test_validate_bcb_series_rejects_duplicates() -> None:
    dataframe = pd.DataFrame(
        {
            "series_id": [432, 432],
            "observation_date": pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-01-01",
                ]
            ),
            "value": [12.25, 12.25],
        }
    )

    with pytest.raises(DataQualityError, match="duplicados"):
        validate_bcb_series(
            dataframe=dataframe,
            expected_series_id=432,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 10),
        )


def test_validate_bcb_series_rejects_null_values() -> None:
    dataframe = pd.DataFrame(
        {
            "series_id": [432, 432],
            "observation_date": pd.to_datetime(
                [
                    "2025-01-01",
                    "2025-01-02",
                ]
            ),
            "value": [12.25, None],
        }
    )

    with pytest.raises(DataQualityError, match="valores nulos"):
        validate_bcb_series(
            dataframe=dataframe,
            expected_series_id=432,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 10),
        )
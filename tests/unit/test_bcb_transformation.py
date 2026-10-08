from datetime import date

import pandas as pd

from financial_pipeline.transformation.bcb import filter_bcb_series_period


def test_filter_bcb_series_period_removes_out_of_range_records() -> None:
    dataframe = pd.DataFrame(
        {
            "series_id": [24363, 24363, 24363, 24363],
            "observation_date": pd.to_datetime(
                [
                    "2026-06-01",
                    "2026-07-01",
                    "2026-08-01",
                    "2026-09-01",
                ]
            ),
            "value": [145.0, 146.0, 147.0, 148.0],
        }
    )

    result = filter_bcb_series_period(
        dataframe=dataframe,
        start_date=date(2026, 6, 24),
        end_date=date(2026, 8, 15),
    )

    assert result["observation_date"].tolist() == [
        pd.Timestamp("2026-07-01"),
        pd.Timestamp("2026-08-01"),
    ]

    assert len(result) == 2
    assert len(dataframe) == 4
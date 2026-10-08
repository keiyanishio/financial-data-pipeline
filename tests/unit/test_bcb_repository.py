from unittest.mock import MagicMock

from sqlalchemy import Engine

from financial_pipeline.database.bcb_repository import get_active_bcb_series_ids

def test_get_active_bcb_series_ids() -> None:
    database_engine = MagicMock(spec=Engine)

    connection = (
        database_engine
        .connect
        .return_value
        .__enter__
        .return_value
    )

    connection.execute.return_value.scalars.return_value.all.return_value = [1, 11, 432, 24363, 24364]

    result = get_active_bcb_series_ids(engine=database_engine)

    assert result == [1, 11, 432, 24363, 24364]

    database_engine.connect.assert_called_once()
    connection.execute.assert_called_once()
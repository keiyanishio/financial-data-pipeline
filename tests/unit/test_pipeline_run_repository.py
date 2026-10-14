from datetime import date
from unittest.mock import MagicMock
import pytest
from sqlalchemy import Engine

from financial_pipeline.database.pipeline_run_repository import create_bcb_pipeline_run, mark_bcb_pipeline_run_failed, mark_bcb_pipeline_run_success



def create_mock_engine() -> tuple[MagicMock, MagicMock]:
    database_engine = MagicMock(spec=Engine)

    connection = (
        database_engine
        .begin
        .return_value
        .__enter__
        .return_value
    )

    return database_engine, connection


def test_create_bcb_pipeline_run() -> None:
    database_engine, connection = create_mock_engine()

    connection.execute.return_value.scalar_one.return_value = 10

    result = create_bcb_pipeline_run(
        series_id=432,
        requested_start_date=date(2026, 10, 6),
        requested_end_date=date(2026, 10, 13),
        airflow_run_id="manual_test",
        engine=database_engine,
    )

    assert result == 10

    database_engine.begin.assert_called_once()
    connection.execute.assert_called_once()

    parameters = connection.execute.call_args.args[1]

    assert parameters == {
        "series_id": 432,
        "airflow_run_id": "manual_test",
        "requested_start_date": date(2026, 10, 6),
        "requested_end_date": date(2026, 10, 13),
    }


def test_mark_bcb_pipeline_run_success() -> None:
    database_engine, connection = create_mock_engine()

    connection.execute.return_value.rowcount = 1

    mark_bcb_pipeline_run_success(
        run_id=10,
        rows_loaded=8,
        engine=database_engine,
    )

    database_engine.begin.assert_called_once()
    connection.execute.assert_called_once()

    parameters = connection.execute.call_args.args[1]

    assert parameters == {
        "run_id": 10,
        "rows_loaded": 8,
    }


def test_mark_bcb_pipeline_run_failed() -> None:
    database_engine, connection = create_mock_engine()

    connection.execute.return_value.rowcount = 1

    mark_bcb_pipeline_run_failed(
        run_id=10,
        error_message="Falha de teste",
        engine=database_engine,
    )

    database_engine.begin.assert_called_once()
    connection.execute.assert_called_once()

    parameters = connection.execute.call_args.args[1]

    assert parameters == {
        "run_id": 10,
        "error_message": "Falha de teste",
    }


def test_mark_bcb_pipeline_run_success_rejects_unknown_run_id() -> None:
    database_engine, connection = create_mock_engine()

    connection.execute.return_value.rowcount = 0

    with pytest.raises(ValueError, match="Execução de auditoria não encontrada: 999"):
        mark_bcb_pipeline_run_success(run_id=999, rows_loaded=8, engine=database_engine)
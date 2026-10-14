from datetime import date

from sqlalchemy import Engine, text

from financial_pipeline.database.connection import get_engine


CREATE_BCB_PIPELINE_RUN_SQL = text(
    """
    INSERT INTO audit.bcb_pipeline_runs (
        series_id,
        airflow_run_id,
        requested_start_date,
        requested_end_date
    )
    VALUES (
        :series_id,
        :airflow_run_id,
        :requested_start_date,
        :requested_end_date
    )
    RETURNING run_id
    """
)

MARK_BCB_PIPELINE_RUN_SUCCESS_SQL = text(
    """
    UPDATE audit.bcb_pipeline_runs
    SET
        status = 'SUCCESS',
        rows_loaded = :rows_loaded,
        error_message = NULL,
        finished_at = CURRENT_TIMESTAMP
    WHERE run_id = :run_id
    """
)

MARK_BCB_PIPELINE_RUN_FAILED_SQL = text(
    """
    UPDATE audit.bcb_pipeline_runs
    SET
        status = 'FAILED',
        error_message = :error_message,
        finished_at = CURRENT_TIMESTAMP
    WHERE run_id = :run_id
    """
)


def create_bcb_pipeline_run(
    series_id: int,
    requested_start_date: date,
    requested_end_date: date,
    airflow_run_id: str | None = None,
    engine: Engine | None = None,
) -> int:
    """
    Registra o início do processamento de uma série do BCB.
    """

    database_engine = engine or get_engine()

    with database_engine.begin() as connection:
        run_id = connection.execute(
            CREATE_BCB_PIPELINE_RUN_SQL,
            {
                "series_id": series_id,
                "airflow_run_id": airflow_run_id,
                "requested_start_date": requested_start_date,
                "requested_end_date": requested_end_date,
            },
        ).scalar_one()

    return int(run_id)


def mark_bcb_pipeline_run_success(
    run_id: int,
    rows_loaded: int,
    engine: Engine | None = None,
) -> None:
    """
    Marca uma execução como concluída com sucesso.
    """

    database_engine = engine or get_engine()

    with database_engine.begin() as connection:
        result = connection.execute(
            MARK_BCB_PIPELINE_RUN_SUCCESS_SQL,
            {
                "run_id": run_id,
                "rows_loaded": rows_loaded,
            },
        )

        if result.rowcount != 1:
            raise ValueError(f"Execução de auditoria não encontrada: {run_id}")


def mark_bcb_pipeline_run_failed(
    run_id: int,
    error_message: str,
    engine: Engine | None = None,
) -> None:
    """
    Marca uma execução como concluída com falha.
    """

    database_engine = engine or get_engine()

    with database_engine.begin() as connection:
        result = connection.execute(
            MARK_BCB_PIPELINE_RUN_FAILED_SQL,
            {
                "run_id": run_id,
                "error_message": error_message,
            },
        )

        if result.rowcount != 1:
            raise ValueError(f"Execução de auditoria não encontrada: {run_id}")
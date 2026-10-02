from datetime import date

import pandas as pd
from sqlalchemy import Engine, text

from financial_pipeline.database.connection import get_engine


UPSERT_BCB_SERIES_SQL = text(
    """
    INSERT INTO raw.bcb_series (
        series_id,
        observation_date,
        value,
        source
    )
    VALUES (
        :series_id,
        :observation_date,
        :value,
        :source
    )
    ON CONFLICT (series_id, observation_date)
    DO UPDATE SET
        value = EXCLUDED.value,
        source = EXCLUDED.source,
        ingested_at = CURRENT_TIMESTAMP
    """
)

GET_LATEST_OBSERVATION_DATE_SQL = text(
    """
    SELECT MAX(observation_date)
    FROM raw.bcb_series
    WHERE series_id = :series_id
    """
)

def get_latest_observation_date(series_id: int, engine: Engine | None = None) -> date | None:
    """
    Retorna a data mais recente carregada para uma série.
    """

    database_engine = engine or get_engine()

    with database_engine.connect() as connection:
        latest_date = connection.execute(GET_LATEST_OBSERVATION_DATE_SQL, {"series_id": series_id},).scalar_one_or_none()

    return latest_date




def upsert_bcb_series(dataframe: pd.DataFrame,engine: Engine | None = None) -> int:
    """
    Insere ou atualiza séries do BCB no PostgreSQL.
    """

    required_columns = {
        "series_id",
        "observation_date",
        "value",
    }

    missing_columns = required_columns.difference(dataframe.columns)

    if missing_columns:
        raise ValueError(f"Colunas obrigatórias ausentes: {sorted(missing_columns)}")

    if dataframe.empty:
        return 0

    records = []

    for row in dataframe.itertuples(index=False):
        observation_date = row.observation_date

        if isinstance(observation_date, pd.Timestamp):
            observation_date = observation_date.date()

        if not isinstance(observation_date, date):
            raise ValueError("observation_date deve conter datas válidas")

        records.append(
            {
                "series_id": int(row.series_id),
                "observation_date": observation_date,
                "value": float(row.value),
                "source": "BCB_SGS",
            }
        )

    database_engine = engine or get_engine()

    with database_engine.begin() as connection:
        connection.execute(UPSERT_BCB_SERIES_SQL,records)

    return len(records)
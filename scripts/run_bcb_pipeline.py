from datetime import date, timedelta
from pathlib import Path
import logging
import argparse

from financial_pipeline.logging_config import configure_logging
from financial_pipeline.database.bcb_repository import get_latest_observation_date,upsert_bcb_series, get_active_bcb_series_ids
from financial_pipeline.ingestion.bcb import extract_bcb_series, normalize_bcb_series
from financial_pipeline.storage.local import save_json, save_parquet
from financial_pipeline.quality.bcb import validate_bcb_series
from financial_pipeline.transformation.bcb import filter_bcb_series_period

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

INITIAL_START_DATE = date(2025, 1, 1)
INCREMENTAL_LOOKBACK_DAYS = 7


def calculate_start_date(series_id: int) -> date:
    """
    Calcula a data inicial da carga incremental.
    """

    latest_date = get_latest_observation_date(series_id)

    if latest_date is None:
        return INITIAL_START_DATE

    incremental_start_date = latest_date - timedelta(days=INCREMENTAL_LOOKBACK_DAYS)

    return max(INITIAL_START_DATE, incremental_start_date)


def process_series(series_id: int) -> None:
    start_date = calculate_start_date(series_id)
    end_date = date.today()

    print(f"Iniciando série {series_id}")
    print(f"Período: {start_date} até {end_date}")

    records = extract_bcb_series(series_id, start_date, end_date)

    dataframe = normalize_bcb_series(records, series_id)

    dataframe = filter_bcb_series_period(dataframe, start_date, end_date)

    validate_bcb_series(dataframe=dataframe, expected_series_id=series_id, start_date=start_date, end_date=end_date)

    logger.info(
        "Validações de qualidade concluídas | série=%s | linhas=%s",
        series_id,
        len(dataframe),
    )

    period = f"{start_date}_{end_date}"

    raw_path = (
            DATA_DIR
            / "raw"
            / "bcb"
            / f"series_{series_id}"
            / f"{period}.json"
    )

    processed_path = (
            DATA_DIR
            / "processed"
            / "bcb"
            / f"series_{series_id}"
            / f"{period}.parquet"
    )

    save_json(records, raw_path)
    save_parquet(dataframe, processed_path)

    loaded_rows = upsert_bcb_series(dataframe)

    print(f"JSON bruto: {raw_path}")
    print(f"Parquet tratado: {processed_path}")
    print(f"Linhas processadas: {loaded_rows}")
    logger.info(
        "Iniciando série %s | período=%s até %s",
        series_id,
        start_date,
        end_date,
    )

    logger.info(
        "Série %s concluída | linhas=%s | json=%s | parquet=%s",
        series_id,
        loaded_rows,
        raw_path,
        processed_path,
    )
    print("\n\n")

def parse_args() -> argparse.Namespace:
    """
    Lê os argumentos recebidos pela linha de comando.
    """

    parser = argparse.ArgumentParser(description="Executa a ingestão de séries do BCB.")

    parser.add_argument("--series-id", type=int, help="Código de uma série ativa do catálogo para processamento individual.")

    return parser.parse_args()



def main(series_id: int | None = None) -> None:
    configure_logging()

    active_series_ids = get_active_bcb_series_ids()

    if not active_series_ids:
        raise ValueError(
            "Nenhuma série ativa foi encontrada no catálogo do BCB"
        )

    if series_id is not None:
        if series_id not in active_series_ids:
            raise ValueError(
                f"A série {series_id} não está ativa no catálogo do BCB"
            )

        series_ids = [series_id]
    else:
        series_ids = active_series_ids

    logger.info(
        "Séries selecionadas para processamento | séries=%s",
        series_ids,
    )

    for selected_series_id in series_ids:
        try:
            process_series(selected_series_id)

        except Exception:
            logger.exception(
                "Falha no processamento da série %s",
                selected_series_id,
            )
            raise

if __name__ == "__main__":
    arguments = parse_args()
    main(series_id=arguments.series_id)
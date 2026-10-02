from datetime import date, timedelta
from pathlib import Path

from financial_pipeline.database.bcb_repository import get_latest_observation_date,upsert_bcb_series
from financial_pipeline.ingestion.bcb import extract_bcb_series, normalize_bcb_series
from financial_pipeline.storage.local import save_json, save_parquet



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

    period = f"{start_date}_{end_date}"

    raw_path = Path(f"data/raw/bcb/series_{series_id}/{period}.json")

    processed_path = Path(f"data/processed/bcb/series_{series_id}/{period}.parquet")

    save_json(records, raw_path)
    save_parquet(dataframe, processed_path)

    loaded_rows = upsert_bcb_series(dataframe)

    print(f"JSON bruto: {raw_path}")
    print(f"Parquet tratado: {processed_path}")
    print(f"Linhas processadas: {loaded_rows}")
    print()


def main() -> None:
    BCB_SERIES_IDS = [11, 432]
    for series_id in BCB_SERIES_IDS:
        process_series(series_id)


if __name__ == "__main__":
    main()
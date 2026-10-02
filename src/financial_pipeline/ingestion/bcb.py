from datetime import date
from typing import Any

import pandas as pd
import requests


BCB_API_URL = (
    "https://api.bcb.gov.br/dados/serie/"
    "bcdata.sgs.{series_id}/dados"
)


def extract_bcb_series(series_id: int, start_date: date, end_date: date) -> list[dict[str, Any]]:
    """
    Extrai os registros originais da API SGS do Banco Central.
    """

    if start_date > end_date:
        raise ValueError("start_date não pode ser maior que end_date")

    url = BCB_API_URL.format(series_id=series_id)

    params = {
        "formato": "json",
        "dataInicial": start_date.strftime("%d/%m/%Y"),
        "dataFinal": end_date.strftime("%d/%m/%Y"),
    }

    response = requests.get(url,params=params,timeout=30)

    response.raise_for_status()

    records = response.json()

    if not isinstance(records, list):
        raise ValueError("A resposta da API do BCB não é uma lista")

    if not records:
        raise ValueError("A API do BCB não retornou dados para o período")

    return records


def normalize_bcb_series(records: list[dict[str, Any]],series_id: int) -> pd.DataFrame:
    """
    Normaliza os registros do BCB para o formato tabular do projeto.
    """

    dataframe = pd.DataFrame(records)

    required_columns = {"data", "valor"}

    if not required_columns.issubset(dataframe.columns):
        raise ValueError("A resposta do BCB não contém as colunas data e valor")

    dataframe = dataframe.rename(columns={"data": "observation_date","valor": "value"})

    dataframe["observation_date"] = pd.to_datetime(dataframe["observation_date"],format="%d/%m/%Y",errors="raise")

    dataframe["value"] = pd.to_numeric(dataframe["value"],errors="raise")

    dataframe["series_id"] = series_id

    dataframe = dataframe[["series_id", "observation_date", "value"]]

    dataframe = (dataframe.drop_duplicates(subset=["series_id", "observation_date"]).sort_values("observation_date").reset_index(drop=True))

    return dataframe


def fetch_bcb_series(series_id: int,start_date: date, end_date: date) -> pd.DataFrame:
    """
    Executa a extração e a normalização da série.
    """

    records = extract_bcb_series(series_id=series_id,start_date=start_date,end_date=end_date)

    return normalize_bcb_series(records=records,series_id=series_id)
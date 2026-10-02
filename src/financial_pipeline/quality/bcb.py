from datetime import date
from math import isfinite

import pandas as pd


class DataQualityError(ValueError):
    """
    Erro levantado quando os dados falham nas validações de qualidade.
    """


def validate_bcb_series(dataframe: pd.DataFrame, expected_series_id: int, start_date: date, end_date: date):
    """
    Valida a estrutura e o conteúdo de uma série do BCB.
    """

    required_columns = {
        "series_id",
        "observation_date",
        "value",
    }

    missing_columns = required_columns.difference(dataframe.columns)

    if missing_columns:
        raise DataQualityError(f"Colunas ausentes: {sorted(missing_columns)}")

    if dataframe.empty:
        raise DataQualityError("O DataFrame não contém registros")

    if dataframe[list(required_columns)].isnull().any().any():
        raise DataQualityError("Foram encontrados valores nulos")

    if dataframe.duplicated(subset=["series_id", "observation_date"]).any():
        raise DataQualityError("Foram encontrados registros duplicados")

    observed_series_ids = set(dataframe["series_id"].unique())

    if observed_series_ids != {expected_series_id}:
        raise DataQualityError("O DataFrame contém series_id inesperado")

    if not pd.api.types.is_datetime64_any_dtype(dataframe["observation_date"]):
        raise DataQualityError("observation_date não possui tipo datetime")

    if not pd.api.types.is_numeric_dtype(dataframe["value"]):
        raise DataQualityError("value não possui tipo numérico")

    if not dataframe["value"].map(isfinite).all():
        raise DataQualityError("value contém valores infinitos")

    observation_dates = dataframe["observation_date"].dt.date

    if (observation_dates < start_date).any():
        raise DataQualityError("Existem observações anteriores ao período solicitado")

    if (observation_dates > end_date).any():
        raise DataQualityError("Existem observações posteriores ao período solicitado")
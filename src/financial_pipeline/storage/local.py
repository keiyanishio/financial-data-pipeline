import json
from pathlib import Path
from typing import Any

import pandas as pd


def save_json(records: list[dict[str, Any]],file_path: Path) -> Path:
    """
    Salva os registros brutos em JSON.
    """

    file_path.parent.mkdir(parents=True,exist_ok=True)

    with file_path.open(mode="w", encoding="utf-8") as file:
        json.dump(records,file,ensure_ascii=False,indent=2)

    return file_path


def save_parquet(dataframe: pd.DataFrame,file_path: Path) -> Path:
    """
    Salva um DataFrame em formato Parquet.
    """

    file_path.parent.mkdir(parents=True,exist_ok=True)

    dataframe.to_parquet(file_path,index=False)

    return file_path
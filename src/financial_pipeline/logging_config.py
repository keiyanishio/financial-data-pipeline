import logging
import os
from logging.config import dictConfig
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

airflow_home = os.getenv("AIRFLOW_HOME")

if airflow_home:
    LOG_DIRECTORY = (
        Path(airflow_home)
        / "logs"
        / "financial_pipeline"
    )
else:
    LOG_DIRECTORY = PROJECT_ROOT / "logs"

LOG_FILE = LOG_DIRECTORY / "financial_pipeline.log"


def configure_logging() -> None:
    """
    Configura logs no console e em arquivo rotativo.
    """

    LOG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": (
                        "%(asctime)s | "
                        "%(levelname)s | "
                        "%(name)s | "
                        "%(message)s"
                    )
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": "INFO",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "standard",
                    "level": "INFO",
                    "filename": str(LOG_FILE),
                    "maxBytes": 5_000_000,
                    "backupCount": 3,
                    "encoding": "utf-8",
                },
            },
            "root": {
                "handlers": [
                    "console",
                    "file",
                ],
                "level": "INFO",
            },
        }
    )
import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL


load_dotenv()


def get_required_env(variable_name: str) -> str:
    value = os.getenv(variable_name)

    if not value:
        raise ValueError(f"A variável de ambiente {variable_name} não foi definida")

    return value


@lru_cache
def get_engine() -> Engine:
    """
    Cria e reutiliza a conexão do SQLAlchemy com o PostgreSQL.
    """

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=get_required_env("POSTGRES_USER"),
        password=get_required_env("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=get_required_env("POSTGRES_DB"),
    )

    return create_engine(database_url,pool_pre_ping=True,)
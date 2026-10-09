from datetime import timedelta

import pendulum
from airflow.sdk import DAG, task
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_ROOT = "/opt/airflow/project"


default_args = {
    "owner": "keiya",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


@task(task_id="get_active_series")
def build_ingestion_commands() -> list[str]:
    """
    Cria um comando de ingestão para cada série ativa do catálogo.
    """

    from financial_pipeline.database.bcb_repository import get_active_bcb_series_ids

    series_ids = get_active_bcb_series_ids()

    if not series_ids:
        raise ValueError("Nenhuma série ativa foi encontrada no catálogo do BCB")

    return [f"python {PROJECT_ROOT}/scripts/run_bcb_pipeline.py --series-id {series_id}" for series_id in series_ids]


with DAG(
    dag_id="bcb_financial_pipeline",
    description=("Ingestão das séries do BCB e transformação analítica com dbt."),
    start_date=pendulum.datetime(2026, 10, 1, tz="America/Sao_Paulo"),
    schedule="*/30 8-19 * * 1-5",
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["bcb", "financial-data", "dbt"]
) as dag:

    ingestion_commands = build_ingestion_commands()

    ingest_bcb = BashOperator.partial(task_id="ingest_bcb", cwd=PROJECT_ROOT, do_xcom_push=False).expand(bash_command=ingestion_commands)

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "dbt build "
            "--project-dir /opt/airflow/project/dbt "
            "--profiles-dir /opt/airflow/project/dbt"
        ),
        cwd=PROJECT_ROOT,
    )

    ingest_bcb >> dbt_build
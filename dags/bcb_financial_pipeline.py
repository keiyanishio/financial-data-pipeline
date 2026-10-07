from datetime import timedelta

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_ROOT = "/opt/airflow/project"


default_args = {
    "owner": "keiya",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="bcb_financial_pipeline",
    description="Ingestão das séries do BCB e transformação analítica com dbt.",
    start_date=pendulum.datetime(2026, 10, 1, tz="America/Sao_Paulo",),
    schedule="*/10 8-19 * * 1-5",
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["bcb", "financial-data", "dbt"]
) as dag:

    ingest_bcb = BashOperator(
        task_id="ingest_bcb",
        bash_command=("python /opt/airflow/project/scripts/run_bcb_pipeline.py"),
        cwd=PROJECT_ROOT
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=("dbt build --project-dir /opt/airflow/project/dbt --profiles-dir /opt/airflow/project/dbt"),
        cwd=PROJECT_ROOT
    )

    ingest_bcb >> dbt_build
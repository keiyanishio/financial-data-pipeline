import os
from datetime import timedelta

import pendulum
from airflow.sdk import DAG, task
from airflow.providers.smtp.notifications.smtp import send_smtp_notification
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_ROOT = "/opt/airflow/project"


default_args = {
    "owner": "keiya",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

failure_notification = send_smtp_notification(
    smtp_conn_id="smtp_default",
    to=os.environ["AIRFLOW_ALERT_EMAIL"],
    from_email=os.environ["AIRFLOW_SMTP_USER"],
    subject="[Airflow] Falha na DAG {{ dag.dag_id }}",
    html_content=(
        "<h3>Falha no pipeline financeiro</h3>"
        "<p><strong>DAG:</strong> {{ dag.dag_id }}</p>"
        "<p><strong>Tarefa:</strong> {{ ti.task_id }}</p>"
        "<p><strong>Execução:</strong> {{ run_id }}</p>"
        "<p><strong>Tentativa:</strong> {{ ti.try_number }}</p>"
        "<p><a href='{{ ti.log_url }}'>Abrir log da tarefa</a></p>"
    ),
)


@task(task_id="get_active_series")
def build_ingestion_task_arguments() -> list[dict]:
    """
    Cria os argumentos de cada tarefa de ingestão.
    """

    from financial_pipeline.database.bcb_repository import (
        get_active_bcb_series_ids,
    )

    series_ids = get_active_bcb_series_ids()

    if not series_ids:
        raise ValueError(
            "Nenhuma série ativa foi encontrada no catálogo do BCB"
        )

    return [
        {
            "bash_command": (
                "python "
                "/opt/airflow/project/scripts/run_bcb_pipeline.py "
                f"--series-id {series_id}"
            ),
            "env": {
                "SERIES_ID": str(series_id),
                "AIRFLOW_RUN_ID": "{{ run_id }}",
            },
        }
        for series_id in series_ids
    ]

with DAG(
    dag_id="bcb_financial_pipeline",
    description=("Ingestão das séries do BCB e transformação analítica com dbt."),
    start_date=pendulum.datetime(2026, 10, 1, tz="America/Sao_Paulo"),
    schedule="*/30 8-19 * * 1-5",
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    on_failure_callback=failure_notification,
    tags=["bcb", "financial-data", "dbt"]
) as dag:

    
    ingestion_task_arguments = build_ingestion_task_arguments()

    ingest_bcb = BashOperator.partial(
        task_id="ingest_bcb",
        cwd=PROJECT_ROOT,
        append_env=True,
        do_xcom_push=False,
        map_index_template="{{ task.env['SERIES_ID'] }}",
    ).expand_kwargs(
        ingestion_task_arguments
    )

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
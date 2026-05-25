from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'ecommerce_daily_pipeline',
    default_args=default_args,
    description='End-to-end e-commerce pipeline (Ingest, Load, Transform)',
    schedule_interval='@daily',
    catchup=False,
    tags=['ecommerce', 'dbt'],
) as dag:

    ingest_task = BashOperator(
        task_id='ingest_to_minio',
        bash_command='cd /opt/airflow/project && python ingest_to_minio.py'
    )

    load_task = BashOperator(
        task_id='load_to_postgres',
        bash_command='cd /opt/airflow/project && python load_to_postgres.py'
    )

    dbt_run_task = BashOperator(
        task_id='dbt_transform',
        bash_command='cd /opt/airflow/project/dwh_transform && dbt run --profiles-dir /opt/airflow/project'
    )

    ingest_task >> load_task >> dbt_run_task
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from main import run_pipeline

with DAG(
    "imdb_reddit_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    # Task 0: Initialize database
    init_db = PostgresOperator(
        task_id="init_db",
        postgres_conn_id="postgres_default",  # make sure this connection exists in Airflow
        sql="/opt/airflow/dags/init.sql"
    )

    # Task 1: Run ETL
    t1 = PythonOperator(
        task_id="run_imdb_etl",
        python_callable=run_pipeline
    )

    # Set dependency: init_db must run before t1
    init_db >> t1

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from main import run_pipeline  

with DAG("imdb_reddit_pipeline",
         start_date=datetime(2025,1,1),
         schedule_interval="@daily",
         catchup=False) as dag:

    t1 = PythonOperator(
        task_id="run_imdb_reddit_etl",
        python_callable=run_pipeline
    )

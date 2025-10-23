from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Imports the extraction and load function from dags/extract_data.py
from extract_data import run_extraction_pipeline


# DAG DEFAULT ARGUMENTS
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 15), 
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# DAG DEFINITION
with DAG(
    dag_id='stock_market_etl_dbt_pipeline',
    default_args=default_args,
    description='ETL Stock Pipeline with Airflow and dbt',
    schedule_interval='0 3 * * 2-6',
    catchup=False,
    tags=['etl', 'data_ingestion', 'dbt'],
) as dag:
    
    # TASK 1: Extract and Load bronze Data (E-L)
    # This task calls the function that handles API request and PostgreSQL load.
    extract_load_task = PythonOperator(
        task_id='extract_and_load_bronze_data',
        python_callable=run_extraction_pipeline,
    )

    # TASK 2: Run dbt Models (T)
    # Executes 'dbt run' to transform the bronze data in PostgreSQL.
    # The path /opt/airflow/dags/dbt_project must match your Docker volume mapping.
    dbt_run_task = BashOperator(
        task_id='run_dbt_transformation_models',
        bash_command='dbt run --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/config', 
    )
    # FLOW DEFINITION: E-L must complete before T starts
    extract_load_task >> dbt_run_task

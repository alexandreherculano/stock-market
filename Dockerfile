FROM apache/airflow:2.8.4-python3.11

RUN pip install --no-cache-dir \
    'apache-airflow-providers-postgres' \
    'dbt-postgres==1.7.0' \
    'pandas' \
    'requests' \
    'yfinance'

ARG AIRFLOW_UID=50000
ENV AIRFLOW_UID=${AIRFLOW_UID}
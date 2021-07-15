#!/bin/bash
airflow connections add "postgres_db" --conn-uri "postgresql+psycopg2://admin:admin@postgres_db:5433/postgres"
airflow connections add "kaggle_api" --conn-uri "http://user:pass@dummy:1234"
airflow variables set dbt_path /opt/dbt
airflow variables set dbt_project kaggle
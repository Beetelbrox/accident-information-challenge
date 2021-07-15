from airflow import DAG
from datetime import datetime

from airflow.hooks.base_hook import BaseHook
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator

from kaggle_elt.kaggle_dbt_source import KaggleDbtSource, read_kaggle_dbt_source_configs
from kaggle_elt.kaggle_dataset_downloader import download_kaggle_file_with_credentials
from kaggle_elt.kaggle_dbt_loader import load_csv_to_postgres

kaggle_api_conn = BaseHook.get_connection("kaggle_api")
kaggle_db_conn = BaseHook.get_connection("postgres_db")

dbt_path = '/opt/dbt' # This should be a variable in airflow

default_args = {'owner': 'airflow', 'start_date': datetime(2021, 1, 1)}

def create_kaggle_dataset_extractor(dataset_table_name: str, dataset_cfg: KaggleDbtSource, download_dir: str = '/tmp') -> PythonOperator:
    table_cfg = dataset_cfg.get_table(dataset_table_name)
    download_path = f'{download_dir}/{dataset_cfg.name}'
    return PythonOperator(
        task_id=f'download_{table_cfg.name}',
        python_callable=download_kaggle_file_with_credentials,
        op_args=[
            dataset_cfg.kaggle_full_name,
            table_cfg.kaggle_file_name,
            kaggle_api_conn.login,
            kaggle_api_conn.password,
            download_path
        ]
    )

def create_kaggle_dataset_loader(dataset_table_name: str, dataset_cfg: KaggleDbtSource, download_dir='/tmp'):
    return PythonOperator(
        task_id=f"load_{dataset_table_name}",
        python_callable=load_csv_to_postgres,
        op_args=[
            kaggle_db_conn,
            dataset_cfg,
            dataset_table_name,
            download_dir
        ]
    )

def create_kaggle_elt_dag(dataset_cfg, schedule, default_args):
    dag = DAG(f'{dataset_cfg.name}_elt',
            schedule_interval=schedule,
            default_args=default_args
    )
    with dag:
        transform_op = BashOperator(
            task_id=f'run_dbt_{dataset_cfg.name}',
            bash_command=f"/home/airflow/.local/bin/dbt --partial-parse ls --project-dir {dbt_path}/kaggle -m {dataset_cfg.name}",
            env={
                'DBT_PROFILES_DIR': dbt_path,
                'DBT_DB_HOST': kaggle_db_conn.host,
                'DBT_DB_USER': kaggle_db_conn.login,
                'DBT_DB_PASSWORD': kaggle_db_conn.password,
                'DWH_PORT': str(kaggle_db_conn.port),
                'DBT_DWH_DBNAME': kaggle_db_conn.schema,
                'DBT_SCHEMA': 'kaggle'
            },
            dag=dag
        )
        for dataset_table_name in dataset_cfg.tables.keys():
            extract_op = create_kaggle_dataset_extractor(dataset_table_name, dataset_cfg)
            loader_op = create_kaggle_dataset_loader(dataset_table_name, dataset_cfg)
            extract_op >> loader_op >> transform_op
    return dag

dataset_configs = read_kaggle_dbt_source_configs(dbt_path)

for dbt_dataset_name, dataset_cfg in dataset_configs.items():
    globals()[dbt_dataset_name] = create_kaggle_elt_dag(dataset_cfg, None, default_args)
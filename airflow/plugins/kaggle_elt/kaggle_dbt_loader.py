import psycopg2

from kaggle_elt.kaggle_dbt_source import KaggleDbtSource
from kaggle_elt.csv_sanitizer import CSVSanitizer
from typing import List

class KaggleDbtTableLoader:
    def __init__(self, kaggle_dbt_source_cfg: KaggleDbtSource, target_table: str, download_dir: str):
        self.source_cfg = kaggle_dbt_source_cfg
        self.target_table = kaggle_dbt_source_cfg.get_table(target_table)
        self.download_dir = download_dir
    
    def _get_table_columns_repr(self, include_types: bool=False) -> List[str]:
        return (c.name + (f' {c.data_type}' if include_types else '') for c in self.target_table.columns.values())

    def _build_create_table_stmt(self) -> str:
        column_reprs = self._get_table_columns_repr(include_types=True)
        return f"CREATE TABLE IF NOT EXISTS {self.target_table.qualified_name} ({','.join(column_reprs)});"
    
    def _build_copy_stmt(self) -> str:
        column_reprs = self._get_table_columns_repr()
        return f"""COPY {self.target_table.qualified_name} ({','.join(column_reprs)}) FROM STDIN WITH
            CSV
            HEADER
            DELIMITER AS '{self.source_cfg.delimiter}'
            NULL AS '{self.source_cfg.null_value}';
        """
    
    def drop_table(self, cursor) -> None:
        print(f'Attempting to drop table {self.target_table.qualified_name}...')
        cursor.execute(f'DROP TABLE IF EXISTS {self.target_table.qualified_name} CASCADE')
        print(f'Done')

    def create_schema(self, cursor) -> None:
        print(f'Attempting to create schema {self.target_table.schema}...')
        create_schema_stmt = f'CREATE schema IF NOT EXISTS {self.target_table.schema};'
        cursor.execute(create_schema_stmt)
        print(f'Done')

    def create_table(self, cursor) -> None:
        print(f'Attempting to create table {self.target_table.qualified_name}...')
        create_table_stmt = self._build_create_table_stmt()
        cursor.execute(create_table_stmt)
        print(f'Done')

    def load_data_from_csv(self, cursor):
        print(f'Attempting to load data from csv into table {self.target_table.qualified_name}...')
        copy_stmt = self._build_copy_stmt()
        print(copy_stmt)
        file_path = f'{self.download_dir}/{self.source_cfg.name}/{self.target_table.kaggle_file_name}'
        with open(file_path, 'r', encoding=self.source_cfg.encoding) as ifile:
            cursor.copy_expert(copy_stmt, CSVSanitizer(ifile, self.target_table.get_kaggle_to_dbt_mapping()))
        print(f'Done')

def load_csv_to_postgres(pg_creds, kaggle_dbt_source_cfg: KaggleDbtSource, target_table: str, download_dir: str = '/tmp'):
    # Build the loader object
    kaggle_table_loader = KaggleDbtTableLoader(kaggle_dbt_source_cfg, target_table, download_dir)
    try:
        # Ducktype the connection
        # Create the connection here to be able to leverage parallelism in airflow, cursors created from the same connection
        # will belong to the same session and will execute statements in series.
        pg_conn = psycopg2.connect(
            host=pg_creds.host,
            dbname=pg_creds.schema,
            user=pg_creds.login,
            password=pg_creds.password,
            port=pg_creds.port
        )
        pg_conn.autocommit = True   # Autocommit to avoid spamming it later
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    with pg_conn.cursor() as cursor:
        kaggle_table_loader.drop_table(cursor)
        kaggle_table_loader.create_schema(cursor)
        kaggle_table_loader.create_table(cursor)
        kaggle_table_loader.load_data_from_csv(cursor)
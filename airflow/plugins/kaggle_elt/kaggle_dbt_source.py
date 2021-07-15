import os
import yaml
from typing import Dict, Any

class KaggleDbtSourceTableColumn:
    def __init__(self, dbt_yaml: Dict[str, Any]):
        self.name = dbt_yaml['name']
        self.data_type = dbt_yaml['data_type']
        self.kaggle_column_name = dbt_yaml['meta']['kaggle_column_name']

class KaggleDbtSourceTable:
    def __init__(self, dbt_yaml: Dict[str, Any], schema: str):
        self.name = dbt_yaml['name']
        self.schema = schema
        self.kaggle_file_name = dbt_yaml['meta']['kaggle_file_name']
        self.columns = {c['name']: KaggleDbtSourceTableColumn(c) for c in dbt_yaml.get('columns', [])}
    
    @property
    def qualified_name(self) -> str:
        return f'{self.schema}.{self.name}'
    
    def get_kaggle_to_dbt_mapping(self) -> Dict[str, str]:
        return {c.kaggle_column_name: c.name for c in self.columns.values()}

class KaggleDbtSource:
    def __init__(self, dbt_yaml: Dict[str, Any]):
        yaml_dbt_source = dbt_yaml['sources'][0]
        self.name = yaml_dbt_source['name']
        self.schema = yaml_dbt_source['schema']
        # Pull the kaggle dataset name & parse it
        kaggle_dataset_owner, kaggle_dataset_name = yaml_dbt_source['meta']['kaggle_dataset'].split('/')
        self.kaggle_owner = kaggle_dataset_owner
        self.kaggle_name = kaggle_dataset_name
        self.delimiter = yaml_dbt_source['meta'].get('delimiter', '|')
        self.null_value = yaml_dbt_source['meta'].get('null_value', 'NA')
        self.encoding = yaml_dbt_source['meta'].get('encoding', 'utf-8')
        # Build the tables. Pass the schema for convenience
        self.tables = {t['name']: KaggleDbtSourceTable(t, self.schema) for t in yaml_dbt_source['tables']}

    @property
    def kaggle_full_name(self) -> str:
        return f'{self.kaggle_owner}/{self.kaggle_name}'
    
    def get_table(self, table_name: str) -> KaggleDbtSourceTable:
        return self.tables[table_name]

def read_kaggle_dbt_source_configs(dbt_project_path: str) -> KaggleDbtSource:
    dbt_source_cfgs = {}
    for ds in os.listdir(f'{dbt_project_path}/kaggle/models/'):
        with open(f'{dbt_project_path}/kaggle/models/{ds}/sources/src_{ds}.yml', 'r') as ifile:
            try:
                dataset_cfg = KaggleDbtSource(yaml.safe_load(ifile))
            except yaml.YAMLError as e:
                print(e)
        dbt_source_cfgs[dataset_cfg.name] = dataset_cfg
    return dbt_source_cfgs
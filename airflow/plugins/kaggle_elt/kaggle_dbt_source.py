import os
import yaml
from typing import Dict, Any

class KaggleDbtSourceTableColumn:
    """A class representig a dbt source column, enriched with the kaggle metadata"""
    def __init__(self, dbt_yaml: Dict[str, Any]):
        """Constructs all necessary attributes for the object from a parsed dby .yml file"""
        self.name = dbt_yaml['name']
        self.data_type = dbt_yaml['data_type']
        self.kaggle_column_name = dbt_yaml['meta']['kaggle_column_name']

class KaggleDbtSourceTable:
    """A class representig a dbt source table, enriched with the kaggle metadata"""
    def __init__(self, dbt_yaml: Dict[str, Any], schema: str):
        """Constructs all necessary attributes for the object from a parsed dby .yml file"""
        self.name = dbt_yaml['name']
        self.schema = schema
        self.kaggle_file_name = dbt_yaml['meta']['kaggle_file_name']
        self.columns = {c['name']: KaggleDbtSourceTableColumn(c) for c in dbt_yaml.get('columns', [])}
    
    @property
    def qualified_name(self) -> str:
        """Returns the qualified name for the source table"""
        return f'{self.schema}.{self.name}'
    
    def get_kaggle_to_dbt_mapping(self) -> Dict[str, str]:
        """Gets the mapping from the original names in the kaggle dataset to the sanitized names"""
        return {c.kaggle_column_name: c.name for c in self.columns.values()}

class KaggleDbtSource:
    """A class representig a dbt source, enriched with the kaggle metadata. Can contain one or more tables"""
    def __init__(self, dbt_yaml: Dict[str, Any]):
        """Constructs all necessary attributes for the object from a parsed dby .yml file"""
        yaml_dbt_source = dbt_yaml['sources'][0]
        self.name = yaml_dbt_source['name']
        self.schema = yaml_dbt_source['schema']
        # Pull the kaggle dataset name & parse it
        kaggle_dataset_owner, kaggle_dataset_name = yaml_dbt_source['meta']['kaggle_dataset'].split('/')
        self.kaggle_owner = kaggle_dataset_owner
        self.kaggle_name = kaggle_dataset_name
        # Configs for the CSV
        self.delimiter = yaml_dbt_source['meta'].get('delimiter', '|')
        self.null_value = yaml_dbt_source['meta'].get('null_value', 'NA')
        self.encoding = yaml_dbt_source['meta'].get('encoding', 'utf-8')
        # Build the tables. Pass the schema for convenience
        self.tables = {t['name']: KaggleDbtSourceTable(t, self.schema) for t in yaml_dbt_source['tables']}

    @property
    def kaggle_full_name(self) -> str:
        """Build the full Kaggle dataset name"""
        return f'{self.kaggle_owner}/{self.kaggle_name}'
    
    def get_table(self, table_name: str) -> KaggleDbtSourceTable:
        """Returns a given table"""
        return self.tables[table_name]

def read_kaggle_dbt_source_configs(dbt_project_path: str, dbt_project_name: str) -> KaggleDbtSource:
    """Reads and parses all dbt source configuration files (with the right naming) in a dbt project"""
    dbt_source_cfgs = {}
    dbt_models_path = f'{dbt_project_path}/{dbt_project_name}/models'
    for ds in os.listdir(dbt_models_path):
        with open(f'{dbt_models_path}/{ds}/sources/src_{ds}.yml', 'r') as ifile:
            try:
                dataset_cfg = KaggleDbtSource(yaml.safe_load(ifile))
            except yaml.YAMLError as e:
                print(e)
        dbt_source_cfgs[dataset_cfg.name] = dataset_cfg
    return dbt_source_cfgs
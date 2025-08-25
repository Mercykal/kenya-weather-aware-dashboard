from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import Postgres
from pandas import DataFrame
from os import path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data_to_postgres(data: dict, **kwargs) -> None:
    """
    Exports a dictionary of DataFrames to PostgreSQL using Mage's native connector.
    It reads the configuration from 'io_config.yaml'.
    """
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    
    for table_name, df in data.items():
        if df is not None and isinstance(df, DataFrame) and not df.empty:
            print(f"Preparing to export data to table: {table_name}")
            with Postgres.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
                
                # --- THE FIX: Manually drop the table before exporting ---
                # 'DROP TABLE IF EXISTS' is a safe command. It will only drop the
                # table if it's there, and won't cause an error if it's not.
                print(f"Dropping table '{table_name}' if it exists...")
                loader.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE;')
                print(f"Table '{table_name}' dropped.")

                # Now, export the data to a fresh table
                print(f"Exporting data to new '{table_name}' table...")
                loader.export(
                    df,
                    None,  # schema_name
                    table_name,
                    index=False,
                    # We can change this to 'append' now since we know the table is empty,
                    # but 'replace' is also fine. Let's use 'append' for clarity.
                    if_exists='append',
                )
                print(f"Successfully exported data to table: {table_name}")
        else:
            print(f"Skipping table '{table_name}' as no data was provided.")
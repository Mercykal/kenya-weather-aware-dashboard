from sqlalchemy import create_engine
import os

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Create the database connection URL and the SQLAlchemy engine
# The engine is the entry point to the database for SQLAlchemy.

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_engine(DATABASE_URL)


@data_exporter
def export_data(data, *args, **kwargs):
    """
    Template for exporting data to a SQL database.
    """
    # The 'data' variable contains the final DataFrames
    
    # Define table names to loop through
    table_mappings = {
        "weather_forecasts": data.get("weather_forecasts"),
        "products": data.get("products"),
        "customers": data.get("customers"),
        "orders": data.get("orders")
    }

    # --- Database Connection ---
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DATABASE_URL)

    # Loop through the dictionary and save each DataFrame to its table
    for table_name, df in table_mappings.items():
        if not df.empty:
            print(f"Loading data into '{table_name}' table...")
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Successfully loaded '{table_name}'.")
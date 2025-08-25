import os
import pandas as pd
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Import the data fetching functions from your first script
from data_extraction import fetch_weather_data, fetch_product_data, fetch_customer_data, CITIES

# --- Database Connection Setup ---
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Create the database connection URL and the SQLAlchemy engine
# The engine is the entry point to the database for SQLAlchemy.
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

print("Database engine created successfully.")

# --- Data Transformation Functions ---

def transform_weather_data(weather_data_raw):
    """Cleans and transforms raw weather data to match the database schema."""
    if not weather_data_raw:
        return pd.DataFrame()

    df = pd.DataFrame(weather_data_raw)
    
    # Extract nested data into separate columns
    df['temperature'] = df['main'].apply(lambda x: x.get('temp'))
    df['wind_speed_ms'] = df['wind'].apply(lambda x: x.get('speed'))
    # Handle cases where 'rain' data is not present
    df['rainfall_mm'] = df['rain'].apply(lambda x: x.get('3h', 0) if isinstance(x, dict) else 0)
    df['forecast_time'] = pd.to_datetime(df['dt_txt'])
    
    # Select and rename columns to match the 'weather_forecasts' table
    df_transformed = df[['city', 'forecast_time', 'temperature', 'rainfall_mm', 'wind_speed_ms']].copy()
    df_transformed.rename(columns={'city': 'city_name'}, inplace=True) # Renaming to avoid confusion with city table
    
    # Add a primary key
    df_transformed.insert(0, 'forecast_id', range(1, 1 + len(df_transformed)))
    
    print("Weather data transformed successfully.")
    return df_transformed

def transform_product_data(product_data_raw):
    """Cleans and transforms raw product data."""
    if not product_data_raw:
        return pd.DataFrame()
        
    df = pd.DataFrame(product_data_raw)
    
    # Select and rename columns for the 'products' table
    df_transformed = df[['id', 'title', 'price', 'category']].copy()
    df_transformed.rename(columns={'id': 'product_id', 'title': 'name'}, inplace=True)
    
    print("Product data transformed successfully.")
    return df_transformed

def transform_customer_data(customer_data_raw):
    """Cleans and transforms raw customer data."""
    if not customer_data_raw:
        return pd.DataFrame()

    df = pd.DataFrame(customer_data_raw)
    
    # Extract city from the nested 'address' dictionary
    df['city'] = df['address'].apply(lambda x: x.get('city'))
    
    # Select and rename columns for the 'customers' table
    df_transformed = df[['id', 'firstname', 'lastname', 'email', 'city']].copy()
    df_transformed.rename(columns={'id': 'customer_id', 'firstname': 'first_name', 'lastname': 'last_name'}, inplace=True)
    
    print("Customer data transformed successfully.")
    return df_transformed

def generate_mock_orders(customers_df, products_df, num_orders=200):
    """Generates a DataFrame of mock orders."""
    if customers_df.empty or products_df.empty:
        return pd.DataFrame()

    orders_data = []
    customer_ids = customers_df['customer_id'].tolist()
    product_ids = products_df['product_id'].tolist()
    delivery_statuses = ['Delivered', 'Shipped', 'On Time', 'Delayed', 'Cancelled']
    
    for i in range(1, num_orders + 1):
        orders_data.append({
            'order_id': i,
            'customer_id': random.choice(customer_ids),
            'product_id': random.choice(product_ids),
            'order_date': datetime.now() - timedelta(days=random.randint(0, 90)),
            'quantity': random.randint(1, 5),
            'delivery_status': random.choice(delivery_statuses)
        })
        
    print(f"{num_orders} mock orders generated successfully.")
    return pd.DataFrame(orders_data)

# --- Main Execution Block ---

if __name__ == "__main__":
    # 1. EXTRACT raw data using functions from the other script
    print("--- Starting Data Extraction ---")
    api_key = os.getenv("OPENWEATHER_API_KEY")
    weather_raw = fetch_weather_data(api_key, CITIES)
    products_raw = fetch_product_data()
    customers_raw = fetch_customer_data()
    
    # 2. TRANSFORM the raw data into clean DataFrames
    print("\n--- Starting Data Transformation ---")
    weather_df = transform_weather_data(weather_raw)
    products_df = transform_product_data(products_raw)
    customers_df = transform_customer_data(customers_raw)
    orders_df = generate_mock_orders(customers_df, products_df)
    
    # 3. LOAD the clean DataFrames into the PostgreSQL database
    print("\n--- Starting Data Loading ---")
    try:
        # Use .to_sql() to write each DataFrame to a new table
        # if_exists='replace' will drop the table if it already exists and create a new one.
        # This is useful for development and running the script multiple times.
        weather_df.to_sql('weather_forecasts', engine, if_exists='replace', index=False)
        print("Successfully loaded 'weather_forecasts' table.")
        products_df.to_sql('products', engine, if_exists='replace', index=False)
        print("Successfully loaded 'products' table.")
        customers_df.to_sql('customers', engine, if_exists='replace', index=False)
        print("Successfully loaded 'customers' table.")
        orders_df.to_sql('orders', engine, if_exists='replace', index=False)
        print("Successfully loaded 'orders' table.")
        
        print("\nAll data has been loaded into the PostgreSQL database successfully.")
        
    except Exception as e:
        print(f"An error occurred during data loading: {e}")
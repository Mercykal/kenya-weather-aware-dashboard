import pandas as pd
import random
from datetime import datetime, timedelta

# This import is mandatory for any transformer block
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer

# --- Helper Transformation Functions ---

# This function remains UNCHANGED
def transform_weather_data(weather_data_raw: list) -> pd.DataFrame:
    """Cleans and transforms raw weather data."""
    if not weather_data_raw:
        return pd.DataFrame()
    df = pd.DataFrame(weather_data_raw)
    df['temperature'] = df['main'].apply(lambda x: x.get('temp'))
    df['wind_speed_ms'] = df['wind'].apply(lambda x: x.get('speed'))
    df['rainfall_mm'] = df['rain'].apply(lambda x: x.get('3h', 0) if isinstance(x, dict) else 0)
    df['forecast_time'] = pd.to_datetime(df['dt_txt'])
    df_transformed = df[['city', 'forecast_time', 'temperature', 'rainfall_mm', 'wind_speed_ms']].copy()
    df_transformed.rename(columns={'city': 'city_name'}, inplace=True)
    df_transformed.insert(0, 'forecast_id', range(1, 1 + len(df_transformed)))
    print("Weather data transformed successfully.")
    return df_transformed

# This function remains UNCHANGED
def transform_product_data(product_data_raw: list) -> pd.DataFrame:
    """Cleans and transforms raw product data."""
    if not product_data_raw:
        return pd.DataFrame()
    df = pd.DataFrame(product_data_raw)
    df_transformed = df[['id', 'title', 'price', 'category']].copy()
    df_transformed.rename(columns={'id': 'product_id', 'title': 'name'}, inplace=True)
    print("Product data transformed successfully.")
    return df_transformed

# --- THIS IS THE MODIFIED FUNCTION ---
def transform_customer_data(customer_data_raw: list) -> pd.DataFrame:
    """Cleans and transforms raw customer data, assigning Kenyan cities."""
    if not customer_data_raw:
        return pd.DataFrame()

    df = pd.DataFrame(customer_data_raw)
    
    # Define the list of actual Kenyan cities for the project.
    kenyan_cities = ["Nairobi", "Mombasa", "Kisumu", "Eldoret", "Nakuru"]
    
    # Create a new 'city' column by randomly assigning a city from the list to each row.
    # This OVERWRITES the fake city data that came from the API.
    df['city'] = [random.choice(kenyan_cities) for _ in range(len(df))]

    # The rest of the function remains the same.
    df_transformed = df[['id', 'firstname', 'lastname', 'email', 'city']].copy()
    df_transformed.rename(columns={'id': 'customer_id', 'firstname': 'first_name', 'lastname': 'last_name'}, inplace=True)
    
    print("Customer data transformed successfully with Kenyan cities.")
    return df_transformed
# --- END OF MODIFIED FUNCTION ---

# This function remains UNCHANGED
def generate_mock_orders(customers_df: pd.DataFrame, products_df: pd.DataFrame, num_orders: int = 200) -> pd.DataFrame:
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

# This main decorated function remains UNCHANGED
@transformer
def transform_data(data: dict, *args, **kwargs) -> dict:
    """
    Takes the raw data from the loader, transforms it, generates mock orders,
    and returns a dictionary of clean DataFrames.
    """
    weather_df = transform_weather_data(data.get('weather'))
    products_df = transform_product_data(data.get('products'))
    customers_df = transform_customer_data(data.get('customers'))
    orders_df = generate_mock_orders(customers_df, products_df)

    print("All data transformed and mock orders generated.")

    return {
        "weather_forecasts": weather_df,
        "products": products_df,
        "customers": customers_df,
        "orders": orders_df
    }
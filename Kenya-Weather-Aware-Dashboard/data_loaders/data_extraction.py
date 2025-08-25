import os
import requests
import pandas as pd
from dotenv import load_dotenv

# --- Setup ---
# This line looks for a .env file in the parent directory of this script
# and loads the environment variables from it (e.g., OPENWEATHER_API_KEY)
# Let the library find the .env file automatically
load_dotenv()
print(f"Current Directory: {os.getcwd()}")

# --- Constants ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/forecast"
FAKE_STORE_API_URL = "https://fakestoreapi.com/products"
# We will get 50 customers for this demonstration.
FAKER_API_CUSTOMERS_URL = "https://fakerapi.it/api/v1/persons?_quantity=50"

# Latitude and longitude for the target cities, as specified in the project
CITIES = {
    "Nairobi": {"lat": -1.2921, "lon": 36.8219},
    "Mombasa": {"lat": -4.0435, "lon": 39.6682},
    "Kisumu": {"lat": -0.1022, "lon": 34.7617},
    "Eldoret": {"lat": 0.5143, "lon": 35.2698},
    "Nakuru": {"lat": -0.3031, "lon": 36.0800}
}

# --- Data Fetching Functions ---

def fetch_weather_data(api_key, cities):
    """
    Fetches 5-day/3-hour weather forecast for multiple cities from OpenWeather API.
    Returns a list of all forecast entries.
    """
    all_forecasts = []
    print("Fetching weather data...")

    if not api_key:
        print("Error: OPENWEATHER_API_KEY not found. Please check your .env file.")
        return None

    for city, coords in cities.items():
        params = {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "appid": api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(OPENWEATHER_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            for forecast in data.get('list', []):
                forecast['city'] = city
            all_forecasts.extend(data.get('list', []))
            print(f"  Successfully fetched weather for {city}.")

        except requests.exceptions.HTTPError as http_err:
            print(f"  HTTP error fetching weather for {city}: {http_err} - Check your API key and permissions.")
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching weather for {city}: {e}")
    
    print("Weather data fetching complete.")
    return all_forecasts

def fetch_product_data():
    """Fetches product data from the Fake Store API."""
    print("Fetching product data...")
    try:
        response = requests.get(FAKE_STORE_API_URL)
        response.raise_for_status()
        data = response.json()
        print("  Successfully fetched product data.")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching product data: {e}")
        return None

def fetch_customer_data():
    """Fetches mock customer data from FakerAPI."""
    print("Fetching customer data...")
    try:
        response = requests.get(FAKER_API_CUSTOMERS_URL)
        response.raise_for_status()
        data = response.json().get('data', [])
        print("  Successfully fetched customer data.")
        return data
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching customer data: {e}")
        return None

# --- Main Execution Block ---
# THIS IS THE MOST IMPORTANT PART. IF IT'S MISSING, NOTHING HAPPENS.
if __name__ == "__main__":
    weather_data = fetch_weather_data(OPENWEATHER_API_KEY, CITIES)
    product_data = fetch_product_data()
    customer_data = fetch_customer_data()

    if weather_data:
        weather_df = pd.DataFrame(weather_data)
        print("\n--- Weather Data Sample ---")
        print(weather_df.head())
        print(f"\nTotal weather forecasts fetched: {len(weather_df)}")
        
    if product_data:
        products_df = pd.DataFrame(product_data)
        print("\n--- Product Data Sample ---")
        print(products_df.head())
        print(f"\nTotal products fetched: {len(products_df)}")

    if customer_data:
        customers_df = pd.DataFrame(customer_data)
        print("\n--- Customer Data Sample ---")
        print(customers_df.head())
        print(f"\nTotal customers fetched: {len(customers_df)}")
@data_loader
def load_raw_data(*args, **kwargs):
    """
    Template for loading data from API
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    weather_raw = fetch_weather_data(api_key, CITIES)
    products_raw = fetch_product_data()
    customers_raw = fetch_customer_data()

    # Mage can pass multiple outputs to the next block
    # We will return them as a dictionary
    return {
        "weather": weather_raw,
        "products": products_raw,
        "customers": customers_raw
    }
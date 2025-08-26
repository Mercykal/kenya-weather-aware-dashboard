import os
import requests
import pandas as pd
from dotenv import load_dotenv
from mage_ai.settings.repo import get_repo_path

# This import is mandatory for any loader block
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

# --- Correctly load the .env file from the project root ---
# This is crucial for Mage to find your API key
env_path = os.path.join(get_repo_path(), '.env')
load_dotenv(dotenv_path=env_path)

# --- Constants ---
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/forecast"
FAKE_STORE_API_URL = "https://fakestoreapi.com/products"
FAKER_API_CUSTOMERS_URL = "https://fakerapi.it/api/v1/persons?_quantity=50"

CITIES = {
    "Nairobi": {"lat": -1.2921, "lon": 36.8219},
    "Mombasa": {"lat": -4.0435, "lon": 39.6682},
    "Kisumu": {"lat": -0.1022, "lon": 34.7617},
    "Eldoret": {"lat": 0.5143, "lon": 35.2698},
    "Nakuru": {"lat": -0.3031, "lon": 36.0800}
}

# --- Data Fetching Functions ---
# These are your helper functions. They are not decorated.

def fetch_weather_data(api_key, cities):
    """Fetches 5-day/3-hour weather forecast for multiple cities."""
    all_forecasts = []
    print("Fetching weather data...")
    if not api_key:
        raise Exception("Error: OPENWEATHER_API_KEY not found. Please check your .env file setup in the Mage block.")

    for city, coords in cities.items():
        params = {"lat": coords["lat"], "lon": coords["lon"], "appid": api_key, "units": "metric"}
        try:
            response = requests.get(OPENWEATHER_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            for forecast in data.get('list', []):
                forecast['city'] = city
            all_forecasts.extend(data.get('list', []))
            print(f"  Successfully fetched weather for {city}.")
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
        print("  Successfully fetched product data.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching product data: {e}")
        return None

def fetch_customer_data():
    """Fetches mock customer data from FakerAPI."""
    print("Fetching customer data...")
    try:
        response = requests.get(FAKER_API_CUSTOMERS_URL)
        response.raise_for_status()
        print("  Successfully fetched customer data.")
        return response.json().get('data', [])
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching customer data: {e}")
        return None

# --- Main Mage Function ---
# This is the ONLY function that should be decorated.
# Mage will run this function when the block is executed.

@data_loader
def load_raw_data(*args, **kwargs):
    """
    Loads data from OpenWeather, Fake Store, and Faker APIs.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    # Call the helper functions defined above
    weather_raw = fetch_weather_data(api_key, CITIES)
    products_raw = fetch_product_data()
    customers_raw = fetch_customer_data()

    print("Data extraction complete. Returning raw data to the next block.")

    # Return the data as a dictionary so the next block can use it
    return {
        "weather": weather_raw,
        "products": products_raw,
        "customers": customers_raw
    }

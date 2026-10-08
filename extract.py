"""Extract daily weather data for Sri Lankan cities from the Open-Meteo API."""
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://archive-api.open-meteo.com/v1/archive"

# City name -> (latitude, longitude)
CITIES = {
    "Colombo": (6.9271, 79.8612),
    "Kandy": (7.2906, 80.6337),
    "Galle": (6.0535, 80.2210),
    "Jaffna": (9.6615, 80.0255),
    "Nuwara Eliya": (6.9497, 80.7891),
}

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"
RAW_DIR = Path("data/raw")


def fetch_city_weather(city: str, latitude: float, longitude: float) -> pd.DataFrame:
    """Download daily weather for one city and return it as a DataFrame."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Asia/Colombo",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()  # stop with a clear error if the request failed

    data = pd.DataFrame(response.json()["daily"])
    data["city"] = city
    return data


def extract_all() -> pd.DataFrame:
    """Download weather for every city and combine it into one table."""
    frames = []
    for city, (latitude, longitude) in CITIES.items():
        print(f"Fetching {city}...")
        frames.append(fetch_city_weather(city, latitude, longitude))
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    raw_data = extract_all()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RAW_DIR / "weather_raw.csv"
    raw_data.to_csv(output_path, index=False)

    print(f"Saved {len(raw_data)} rows to {output_path}")
    print(raw_data.head())


if __name__ == "__main__":
    main()
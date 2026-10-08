"""Load clean weather data into the PostgreSQL database."""
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

CLEAN_PATH = Path("data/processed/weather_clean.csv")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS daily_weather (
    city        VARCHAR(50)  NOT NULL,
    date        DATE         NOT NULL,
    temp_max_c  NUMERIC(4,1) NOT NULL,
    temp_min_c  NUMERIC(4,1) NOT NULL,
    temp_avg_c  NUMERIC(4,1) NOT NULL,
    rainfall_mm NUMERIC(6,1) NOT NULL,
    month       SMALLINT     NOT NULL,
    PRIMARY KEY (city, date)
);
"""

# "Upsert": insert new rows, update existing ones, so re-running never duplicates data
UPSERT_SQL = """
INSERT INTO daily_weather
    (city, date, temp_max_c, temp_min_c, temp_avg_c, rainfall_mm, month)
VALUES
    (:city, :date, :temp_max_c, :temp_min_c, :temp_avg_c, :rainfall_mm, :month)
ON CONFLICT (city, date) DO UPDATE SET
    temp_max_c  = EXCLUDED.temp_max_c,
    temp_min_c  = EXCLUDED.temp_min_c,
    temp_avg_c  = EXCLUDED.temp_avg_c,
    rainfall_mm = EXCLUDED.rainfall_mm,
    month       = EXCLUDED.month;
"""


def get_engine():
    """Create a database engine from the settings in the .env file."""
    load_dotenv()
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
    )
    return create_engine(url)


def main() -> None:
    clean_data = pd.read_csv(CLEAN_PATH)
    clean_data["date"] = pd.to_datetime(clean_data["date"]).dt.date
    records = clean_data.to_dict("records")

    engine = get_engine()

    # engine.begin() runs everything as one transaction:
    # if anything fails, nothing is saved halfway
    with engine.begin() as connection:
        connection.execute(text(CREATE_TABLE_SQL))
        connection.execute(text(UPSERT_SQL), records)
        total = connection.execute(text("SELECT COUNT(*) FROM daily_weather;")).scalar()

    print(f"Loaded {len(records)} rows. Table daily_weather now has {total} rows.")


if __name__ == "__main__":
    main()
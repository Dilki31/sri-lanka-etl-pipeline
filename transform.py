"""Transform raw weather data into a clean, analysis-ready table."""
from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/weather_raw.csv")
PROCESSED_DIR = Path("data/processed")

COLUMN_NAMES = {
    "time": "date",
    "temperature_2m_max": "temp_max_c",
    "temperature_2m_min": "temp_min_c",
    "precipitation_sum": "rainfall_mm",
}


def transform(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw weather data and add derived columns."""
    df = raw.rename(columns=COLUMN_NAMES).copy()
    rows_start = len(df)

    # 1. Fix data types and tidy text
    df["date"] = pd.to_datetime(df["date"])
    df["city"] = df["city"].str.strip()

    # 2. Remove duplicate city/date records
    df = df.drop_duplicates(subset=["city", "date"])
    duplicates_removed = rows_start - len(df)

    # 3. Remove rows with missing values
    before = len(df)
    df = df.dropna(subset=["temp_max_c", "temp_min_c", "rainfall_mm"])
    missing_removed = before - len(df)

    # 4. Remove impossible readings (validation)
    before = len(df)
    df = df[(df["temp_min_c"] <= df["temp_max_c"]) & (df["rainfall_mm"] >= 0)]
    invalid_removed = before - len(df)

    # 5. Add derived columns
    df["temp_avg_c"] = ((df["temp_max_c"] + df["temp_min_c"]) / 2).round(1)
    df["month"] = df["date"].dt.month

    df = df.sort_values(["city", "date"]).reset_index(drop=True)

    # Quality report
    print("--- Data quality report ---")
    print(f"Rows at start:           {rows_start}")
    print(f"Duplicates removed:      {duplicates_removed}")
    print(f"Missing-value rows removed: {missing_removed}")
    print(f"Invalid rows removed:    {invalid_removed}")
    print(f"Rows after cleaning:     {len(df)}")

    return df


def main() -> None:
    raw_data = pd.read_csv(RAW_PATH)
    clean_data = transform(raw_data)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "weather_clean.csv"
    clean_data.to_csv(output_path, index=False)

    print(f"Saved clean data to {output_path}")
    print(clean_data.head())


if __name__ == "__main__":
    main()
# Sri Lanka Weather ETL Pipeline

An end-to-end ETL (Extract, Transform, Load) pipeline built with Python and PostgreSQL. It downloads one year of daily weather data for five Sri Lankan cities, cleans and validates it, and loads it into a relational database.

## What it does

1. **Extract:** downloads daily temperature and rainfall for 2025 from the free [Open-Meteo Historical Weather API](https://open-meteo.com/) for Colombo, Kandy, Galle, Jaffna and Nuwara Eliya.
2. **Transform:** renames columns, fixes data types, removes duplicates and missing values, validates readings (for example, minimum temperature must not exceed maximum, and rainfall cannot be negative), and adds average temperature and month columns. A data quality report is printed on every run.
3. **Load:** creates the `daily_weather` table in PostgreSQL and upserts the clean rows, so the pipeline can be re-run safely without creating duplicates.

## Tech stack

Python, Pandas, Requests, SQLAlchemy, PostgreSQL, python-dotenv

## Project structure

```
sri-lanka-etl-pipeline/
├── extract.py          # download raw data from the API
├── transform.py        # clean, validate and enrich the data
├── load.py             # load the clean data into PostgreSQL
├── pipeline.py         # run extract, transform and load with logging
├── test_connection.py  # check the database connection
├── requirements.txt    # Python dependencies
└── .env.example        # example database settings
```

## How to run

1. Clone the repository and create a virtual environment:
```
   git clone https://github.com/Dilki31/sri-lanka-etl-pipeline.git
   cd sri-lanka-etl-pipeline
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
```
2. Create an empty PostgreSQL database named `sl_weather_db`.
3. Copy `.env.example` to `.env` and enter your own database password.
4. Check the connection, then run the pipeline:
```
   python test_connection.py
   python pipeline.py
```

## Results

The pipeline loads 1,825 rows (5 cities x 365 days) into the `daily_weather` table. Running it again keeps the table at 1,825 rows.

Example query:

```sql
SELECT city,
       COUNT(*)                  AS days,
       ROUND(AVG(temp_avg_c), 1) AS avg_temp_c,
       ROUND(SUM(rainfall_mm))   AS total_rain_mm
FROM daily_weather
GROUP BY city
ORDER BY total_rain_mm DESC;
```

| City         | Days | Avg temp (°C) | Total rainfall (mm) |
|--------------|------|---------------|---------------------|
| Galle        | 365  | 26.8          | 3012                |
| Colombo      | 365  | 27.1          | 2828                |
| Nuwara Eliya | 365  | 16.3          | 2530                |
| Kandy        | 365  | 24.5          | 2204                |
| Jaffna       | 365  | 28.1          | 1521                |

## Author

Dilki Ishara Nanayakkara, IT undergraduate at the University of Moratuwa
[GitHub](https://github.com/Dilki31) | [LinkedIn](https://www.linkedin.com/in/dilki-nanayakkara-16b539365)

# Weather ETL Pipeline

An end-to-end Data Engineering project that extracts
weather data from the OpenWeather API, transforms it
using Python, and loads it into PostgreSQL.

## Architecture

OpenWeather API -> JSON -> CSV -> PostgreSQL

## Technologies

- Python
- REST API
- JSON and CSV
- PostgreSQL
- SQL
- Git and GitHub

## Pipeline

1. Extract weather data from the API.
2. Store raw JSON responses.
3. Transform and validate the data.
4. Generate a structured CSV file.
5. Load the records into PostgreSQL.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies from requirements.txt.
3. Configure the required environment variables in `.env`.
4. Create the `weather_db` database and the
   `weather_observations` table.
5. Run the extraction, transformation, and loading scripts.

## Project status

The basic ETL pipeline is functional. Reliability,
automated execution, testing, and analytics are planned
as future improvements.
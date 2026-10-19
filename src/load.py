
import csv
import logging
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


project_dir = Path(__file__).resolve().parent.parent
csv_file = project_dir / "data" / "processed" / "weather.csv"
logs_dir = project_dir / "logs"


def configure_logging():
    """Configura los logs cuando load.py se ejecuta directamente."""
    logs_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                logs_dir / "load.log",
                encoding="utf-8",
            ),
        ],
    )


def run_load():
    """Carga el CSV en PostgreSQL evitando registros duplicados."""
    load_dotenv(project_dir / ".env")

    logging.info("Iniciando carga de datos en PostgreSQL")

    if not csv_file.is_file():
        raise FileNotFoundError(
            f"No se encuentra el archivo CSV: {csv_file}"
        )

    required_vars = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing_vars = [
        name for name in required_vars if not os.getenv(name)
    ]

    if missing_vars:
        raise ValueError(
            "Faltan variables de PostgreSQL en .env: "
            + ", ".join(missing_vars)
        )

    insert_sql = """
        INSERT INTO weather_observations (
            extracted_at,
            city,
            country,
            temperature_c,
            feels_like_c,
            humidity_pct,
            pressure_hpa,
            weather_description,
            wind_speed_m_s,
            cloudiness_pct,
            observed_at_utc
        )
        VALUES (
            %(extracted_at)s,
            %(city)s,
            %(country)s,
            %(temperature_c)s,
            %(feels_like_c)s,
            %(humidity_pct)s,
            %(pressure_hpa)s,
            %(weather_description)s,
            %(wind_speed_m_s)s,
            %(cloudiness_pct)s,
            %(observed_at_utc)s
        )
        ON CONFLICT (extracted_at, city, country)
        DO NOTHING
    """

    conn = None

    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )

        logging.info("Conexión con PostgreSQL establecida")

        inserted = 0
        skipped = 0

        with conn:
            with conn.cursor() as cursor:
                with open(
                    csv_file,
                    "r",
                    encoding="utf-8",
                    newline="",
                ) as file:
                    reader = csv.DictReader(file)

                    if not reader.fieldnames:
                        raise ValueError("El CSV no contiene cabeceras")

                    required_columns = {
                        "extracted_at",
                        "city",
                        "country",
                        "temperature_c",
                        "feels_like_c",
                        "humidity_pct",
                        "pressure_hpa",
                        "weather_description",
                        "wind_speed_m_s",
                        "cloudiness_pct",
                        "observed_at_utc",
                    }

                    missing_columns = required_columns - set(
                        reader.fieldnames
                    )

                    if missing_columns:
                        raise ValueError(
                            "Faltan columnas en el CSV: "
                            + ", ".join(sorted(missing_columns))
                        )

                    for row in reader:
                        cursor.execute(insert_sql, row)

                        if cursor.rowcount == 1:
                            inserted += 1
                        else:
                            skipped += 1

        logging.info(
            "Carga finalizada. Insertados: %s | Omitidos: %s",
            inserted,
            skipped,
        )

    except (psycopg2.Error, OSError, csv.Error, ValueError):
        logging.exception("Error durante la carga de datos")
        raise

    finally:
        if conn is not None:
            conn.close()
            logging.info("Conexión con PostgreSQL cerrada")


if __name__ == "__main__":
    configure_logging()
    try:
        run_load()
    except Exception:
        logging.exception("La carga ha fallado")
        raise

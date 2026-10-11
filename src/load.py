import csv
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

import logging

# 1. CONFIGURACIÓN DE RUTAS Y VARIABLES DE ENTORNO

project_dir = Path(__file__).resolve().parent.parent
csv_file = project_dir / "data" / "processed" / "weather.csv"

load_dotenv(project_dir / ".env")

logs_dir = project_dir / "logs"
logs_dir.mkdir(exist_ok=True)

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

# 2. COMPROBAR QUE EXISTE EL CSV
logging.info("Iniciando carga de datos en PostgreSQL")


if not csv_file.exists():
    logging.error("No se encuentra el archivo CSV: %s", csv_file)
    raise FilenotFoundError(f"No se encuentra el archivo: {csv_file}")

# 3. CONECTAR CON POSTGRESQL

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    logging.info("Conexión con PostgreSQL establecida")

except psycopg2.OperationalError:
    logging.exception("No se pudo conectar con PostgreSQL")
    raise


try:
    # 4. LEER EL CSV E INSERTAR LOS REGISTROS

    with conn:
        with conn.cursor() as cursor:
            with open(csv_file, "r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                inserted = 0
                skipped = 0

                for row in reader:
                    cursor.execute(
                        """
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
                        """,
                        row,    
                    )

                    if cursor.rowcount == 1:
                        inserted += 1
                    else:
                        skipped += 1

                    logging.info(
                        "Carga finalizada. Insertados: %s | Omitidos: %s",
                        inserted,
                        skipped,
                    )
                print(f"Registros insertados: {inserted}")
                print(f"Registros duplicados omitidos: {skipped}")
except psycopg2.Error:
    logging.exception("Error durante la operación en PostgreSQL")
    raise
finally:
    conn.close()
    logging.info("Conexión con PostgreSQL cerrada")
    
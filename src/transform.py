
import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# ==================================================
# 1. CONFIGURACIÓN DE RUTAS
# ==================================================

project_dir = Path(__file__).resolve().parent.parent

raw_dir = project_dir / "data" / "raw"
processed_dir = project_dir / "data" / "processed"
logs_dir = project_dir / "logs"

processed_dir.mkdir(parents=True, exist_ok=True)
logs_dir.mkdir(parents=True, exist_ok=True)

# ==================================================
# 2. CONFIGURACIÓN DEL LOGGING
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            logs_dir / "transform.log",
            encoding="utf-8",
        ),
    ],
)

# ==================================================
# 3. ENCONTRAR LOS ARCHIVOS RAW
# ==================================================

logging.info("Iniciando transformación de datos meteorológicos")

raw_files = sorted(raw_dir.glob("weather_*.json"))

if not raw_files:
    logging.error("No se han encontrado archivos JSON en data/raw")
    raise FileNotFoundError(
        "No se han encontrado archivos JSON en data/raw"
    )

logging.info("Archivos encontrados: %s", len(raw_files))

# ==================================================
# 4. DEFINIR LAS COLUMNAS DEL CSV
# ==================================================

columns = [
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
]

# ==================================================
# 5. TRANSFORMAR Y VALIDAR LOS DATOS
# ==================================================

rows = []
processed = 0
skipped = 0

for raw_file in raw_files:
    logging.info("Procesando archivo: %s", raw_file.name)

    try:
        with open(raw_file, "r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError:
        logging.warning(
            "Archivo descartado: JSON inválido en %s",
            raw_file.name,
        )
        skipped += 1
        continue

    except OSError:
        logging.exception(
            "No se pudo leer el archivo: %s",
            raw_file.name,
        )
        skipped += 1
        continue

    try:
        # Validar la estructura básica del JSON
        if not isinstance(data, dict):
            raise ValueError("El contenido JSON no es un objeto")

        humidity = data["main"]["humidity"]

        if not isinstance(humidity, (int, float)) or isinstance(humidity, bool):
            raise ValueError("La humedad no es un número válido")

        if not 0 <= humidity <= 100:
            raise ValueError(f"Humedad fuera del rango permitido: {humidity}")

        # Convertir la fecha de extracción del nombre del archivo
        extracted_at = datetime.strptime(
            raw_file.stem,
            "weather_%Y-%m-%d_%H-%M-%S",
        ).isoformat()

        # Convertir la fecha de observación de Unix a UTC
        observed_at_utc = datetime.fromtimestamp(
            data["dt"],
            tz=timezone.utc,
        ).isoformat()

        # Crear una fila con los campos que nos interesan
        row = {
            "extracted_at": extracted_at,
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature_c": data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "humidity_pct": humidity,
            "pressure_hpa": data["main"]["pressure"],
            "weather_description": data["weather"][0]["description"],
            "wind_speed_m_s": data["wind"]["speed"],
            "cloudiness_pct": data["clouds"]["all"],
            "observed_at_utc": observed_at_utc,
        }

        rows.append(row)
        processed += 1

    except (KeyError, TypeError, IndexError, ValueError, OverflowError, OSError) as error:
        logging.warning(
            "Archivo descartado: datos ausentes o inválidos en %s. Motivo: %s",
            raw_file.name,
            error,
        )
        skipped += 1
        continue

# ==================================================
# 6. GUARDAR LOS DATOS TRANSFORMADOS
# ==================================================

output_file = processed_dir / "weather.csv"

try:
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

except OSError:
    logging.exception("No se pudo guardar el archivo CSV: %s", output_file)
    raise

# ==================================================
# 7. RESUMEN FINAL
# ==================================================

logging.info("Archivos procesados correctamente: %s", processed)
logging.info("Archivos descartados: %s", skipped)
logging.info("Registros guardados en el CSV: %s", len(rows))
logging.info("Archivo generado: %s", output_file)
logging.info("Transformación finalizada correctamente")

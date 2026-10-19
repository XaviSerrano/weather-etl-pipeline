
import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path


project_dir = Path(__file__).resolve().parent.parent
raw_dir = project_dir / "data" / "raw"
processed_dir = project_dir / "data" / "processed"
logs_dir = project_dir / "logs"

COLUMNS = [
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


def configure_logging():
    """Configura los logs cuando transform.py se ejecuta directamente."""
    logs_dir.mkdir(parents=True, exist_ok=True)

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


def run_transform():
    """Transforma los JSON válidos en un CSV."""
    processed_dir.mkdir(parents=True, exist_ok=True)

    logging.info("Iniciando transformación de datos meteorológicos")

    raw_files = sorted(raw_dir.glob("weather_*.json"))

    if not raw_files:
        raise FileNotFoundError(
            f"No se han encontrado archivos JSON en {raw_dir}"
        )

    logging.info("Archivos encontrados: %s", len(raw_files))

    rows = []
    processed = 0
    skipped = 0

    for raw_file in raw_files:
        logging.info("Procesando archivo: %s", raw_file.name)

        try:
            with open(raw_file, "r", encoding="utf-8") as file:
                data = json.load(file)

        except json.JSONDecodeError:
            logging.warning("JSON inválido en %s", raw_file.name)
            skipped += 1
            continue

        except OSError:
            logging.exception("No se pudo leer %s", raw_file.name)
            skipped += 1
            continue

        try:
            if not isinstance(data, dict):
                raise ValueError("El contenido JSON no es un objeto")

            humidity = data["main"]["humidity"]

            if (
                not isinstance(humidity, (int, float))
                or isinstance(humidity, bool)
                or not 0 <= humidity <= 100
            ):
                raise ValueError(f"Humedad inválida: {humidity}")

            extracted_at = datetime.strptime(
                raw_file.stem,
                "weather_%Y-%m-%d_%H-%M-%S",
            ).isoformat()

            observed_at_utc = datetime.fromtimestamp(
                data["dt"],
                tz=timezone.utc,
            ).isoformat()

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

        except (
            KeyError,
            TypeError,
            IndexError,
            ValueError,
            OverflowError,
        ) as error:
            logging.warning(
                "Datos inválidos en %s: %s",
                raw_file.name,
                error,
            )
            skipped += 1

    # No generar un CSV vacío si todos los archivos han fallado.
    if not rows:
        raise ValueError(
            "No se ha podido generar el CSV: ningún archivo contiene datos válidos"
        )

    output_file = processed_dir / "weather.csv"

    try:
        with open(
            output_file,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)

    except OSError:
        logging.exception("No se pudo guardar el CSV: %s", output_file)
        raise

    logging.info("Archivos procesados correctamente: %s", processed)
    logging.info("Archivos descartados: %s", skipped)
    logging.info("Registros generados: %s", len(rows))
    logging.info("CSV guardado en: %s", output_file)
    logging.info("Transformación finalizada correctamente")


if __name__ == "__main__":
    configure_logging()
    try:
        run_transform()
    except Exception:
        logging.exception("La transformación ha fallado")
        raise


import json
import logging
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


project_dir = Path(__file__).resolve().parent.parent
logs_dir = project_dir / "logs"


def configure_logging():
    """Configura los logs cuando extract.py se ejecuta directamente."""
    logs_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                logs_dir / "extract.log",
                encoding="utf-8",
            ),
        ],
    )


def run_extract():
    """Obtiene los datos de OpenWeather y los guarda en JSON."""
    load_dotenv(project_dir / ".env")
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        raise ValueError(
            "Falta configurar OPENWEATHER_API_KEY en el archivo .env"
        )

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "Barcelona,ES",
        "appid": api_key,
        "units": "metric",
        "lang": "es",
    }

    logging.info("Iniciando extracción de datos meteorológicos")

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.HTTPError:
        logging.exception(
            "Error HTTP de OpenWeather. Código: %s",
            response.status_code,
        )
        raise

    except requests.exceptions.RequestException:
        logging.exception("Error de conexión o petición a OpenWeather")
        raise

    except requests.exceptions.JSONDecodeError:
        logging.exception("La respuesta de OpenWeather no contiene JSON válido")
        raise

    logging.info(
        "Respuesta recibida correctamente. Código HTTP: %s",
        response.status_code,
    )

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"weather_{timestamp}.json"
    filepath = project_dir / "data" / "raw" / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    except OSError:
        logging.exception("No se pudieron guardar los datos en %s", filepath)
        raise

    logging.info("Datos guardados correctamente en: %s", filepath)
    logging.info("Extracción finalizada correctamente")


if __name__ == "__main__":
    configure_logging()
    try:
        run_extract()
    except Exception:
        logging.exception("La extracción ha fallado")
        raise

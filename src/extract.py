
import os
import json
import logging
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


# 1. CONFIGURACIÓN DE RUTAS Y VARIABLES DE ENTORNO

project_dir = Path(__file__).resolve().parent.parent

load_dotenv(project_dir / ".env")

API_KEY = os.getenv("OPENWEATHER_API_KEY")

url = "https://api.openweathermap.org/data/2.5/weather"

params = {
    "q": "Barcelona,ES",
    "appid": API_KEY,
    "units": "metric",
    "lang": "es",
}


# 2. CONFIGURACIÓN DEL LOGGING

logs_dir = project_dir / "logs"
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


# 3. EXTRACCIÓN DE DATOS

logging.info("Iniciando extracción de datos meteorológicos")

if not API_KEY: # Validación temprana: comprobar los requisitos antes de iniciar una operación costosa o dependiente de un servicio externo.
    logging.error("No se ha encontrado OPENWEATHER_API_KEY en el archivo .env")
    raise ValueError("Falta configurar OPENWEATHER_API_KEY")

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

except requests.exceptions.HTTPError:
    logging.exception(
        "La API ha devuelto un error HTTP. Código: %s",
        response.status_code,
    )
    raise

except requests.exceptions.RequestException:
    logging.exception("Error de conexión o de petición a OpenWeather")
    raise

try:
    data = response.json()

except requests.exceptions.JSONDecodeError:
    logging.exception("La respuesta de OpenWeather no contiene JSON válido")
    raise

logging.info(
    "Respuesta de OpenWeather recibida correctamente. Código HTTP: %s",
    response.status_code,
)


# 4. PREPARAR EL ARCHIVO

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"weather_{timestamp}.json"

filepath = project_dir / "data" / "raw" / filename

filepath.parent.mkdir(parents=True, exist_ok=True)


# 5. GUARDAR LOS DATOS RAW

try:
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

except OSError:
    logging.exception("No se pudieron guardar los datos en: %s", filepath)
    raise

logging.info("Datos guardados correctamente en: %s", filepath)
logging.info("Extracción finalizada correctamente")

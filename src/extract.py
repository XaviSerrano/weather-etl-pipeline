import os
import json
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


# 1. CONFIGURACIÓN
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

url = "https://api.openweathermap.org/data/2.5/weather"

params = {
    "q": "Barcelona,ES",
    "appid": API_KEY,
    "units": "metric",
    "lang": "es",
}


# 2. EXTRACCIÓN
response = requests.get(url, params=params, timeout=30)

print(f"Status code: {response.status_code}")

# Si la API devuelve un error, detenemos el programa
response.raise_for_status()

# Convertimos la respuesta JSON en un diccionario de Python
data = response.json()


# 3. PREPARAR EL ARCHIVO
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"weather_{timestamp}.json"

# Localizamos la carpeta raíz del proyecto
project_dir = Path(__file__).resolve().parent.parent

# Construimos la ruta completa del archivo
filepath = project_dir / "data" / "raw" / filename

# Creamos data/raw si todavía no existe
filepath.parent.mkdir(parents=True, exist_ok=True)


# 4. GUARDAR LOS DATOS RAW
with open(filepath, "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f"Datos guardados correctamente en: {filepath}")


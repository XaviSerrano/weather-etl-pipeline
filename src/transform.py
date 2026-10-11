import csv
import json
from datetime import datetime, timezone
from pathlib import Path

# 1. CONFIGURACIÓN DE RUTAS
project_dir = Path(__file__).resolve().parent.parent
raw_dir = project_dir / "data" / "raw" # Carpeta raw
processed_dir = project_dir / "data" / "processed" # Carpeta processed

processed_dir.mkdir(parents=True, exist_ok=True)

# 2. ENCONTRAR LOS ARCHIVOS RAW

raw_files = sorted(raw_dir.glob("weather_*.json"))

if not raw_files:
    raise FileNotFoundError(
        "No se han encontrado archivos JSON en data/raw"
    )

print(f"Archivos encontrados: {len(raw_files)}")

# 3. DEFINIR LAS COLUMNAS DEL CSV

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

# 4. TRANSFORMAR LOS DATOS

rows = []

for raw_file in raw_files:

    print(f"Procesando archivo: {raw_file.name}")

    try:
        with open(raw_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        humidity = data["main"]["humidity"]

        if not 0 <= humidity <= 100:
            print(f"Humedad inválida en {raw_file.name}: {humidity}")
            continue

    except json.JSONDecodeError as error:
        print(f"ERROR: El archivo {raw_file.name} no contiene JSON válido.")
        print(f"Detalle: {error}")
        continue
    
    extracted_at = datetime.strptime(
        raw_file.stem,
        "weather_%Y-%m-%d_%H-%M-%S"
    ).isoformat()

    # Convertir la fecha de observación de Unix a UTC
    observed_at_utc = datetime.fromtimestamp(
        data["dt"],
        tz=timezone.utc
    ).isoformat()

        # Crear una fila con los campos que nos interesan
    row = {
        "extracted_at": extracted_at,
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity_pct": data["main"]["humidity"],
        "pressure_hpa": data["main"]["pressure"],
        "weather_description": data["weather"][0]["description"],
        "wind_speed_m_s": data["wind"]["speed"],
        "cloudiness_pct": data["clouds"]["all"],
        "observed_at_utc": observed_at_utc,
    }

    rows.append(row)

# 5. GUARDAR LOS DATOS TRANSFORMADOS

output_file = processed_dir / "weather.csv"

with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=columns)

    writer.writeheader()
    writer.writerows(rows)

print(f"Transformación completada: {len(rows)} registros")
print(f"Archivo guardado en: {output_file}")
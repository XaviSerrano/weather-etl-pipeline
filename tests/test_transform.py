import csv
import json
from datetime import datetime, timezone

import transform

def test_run_transform_creates_csv_with_valid_data(tmp_path, monkeypatch):

    # tmp_path proporciona una carpeta para trabajar con archivos sin modificar datos reales
    # monkeypatch permite cambiar temporalmente ciertos valores o comportamientos durante el test

    # 1. Prerparamos carpetas temporales para pruebas
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"

    raw_dir.mkdir()

    # 2. Creamos un JSON de ejemplo ficticio con datos meteorológicos válidos.
    raw_file = raw_dir / "weather_2026-10-20_10-30-00.json"

    weather_data = {
        "name": "Barcelona",
        "sys": {"country": "ES"},
        "main": {
            "temp": 20.5,
            "feels_like": 19.8,
            "humidity": 65,
            "pressure": 1015,
        },
        "weather": [{"description": "cielo despejado"}],
        "wind": {"speed": 3.2},
        "clouds": {"all": 10},
        "dt": 1792492200,
    }

    raw_file.write_text(
        json.dumps(weather_data),
        encoding="utf-8",
    )

    # 3. Redirigimos las rutas del módulo a las carpetas temporales.
    monkeypatch.setattr(transform, "raw_dir", raw_dir)
    monkeypatch.setattr(transform, "processed_dir", processed_dir)

    # 4. Ejecutamos la función que queremos probar.
    transform.run_transform()

    # 5. Comprobamos que se ha creado el CSV.
    output_file = processed_dir / "weather.csv"
    assert output_file.exists()

    # 6. Leemos el CSV y comprobamos sus datos.
    with output_file.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["city"] == "Barcelona"
    assert rows[0]["country"] == "ES"
    assert float(rows[0]["temperature_c"]) == 20.5
    assert int(rows[0]["humidity_pct"]) == 65
    assert rows[0]["weather_description"] == "cielo despejado"
    assert rows[0]["extracted_at"] == "2026-10-20T10:30:00"

    expected_observed_at = datetime.fromtimestamp(
        weather_data["dt"],
        tz=timezone.utc,
    ).isoformat()

    assert rows[0]["observed_at_utc"] == expected_observed_at

    print(f"Carpeta temporal: {tmp_path}")

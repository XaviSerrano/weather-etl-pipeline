import csv
import json
from datetime import datetime, timezone

import transform

import pytest

import logging

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

def test_run_transform_skips_invalid_humidity(tmp_path, monkeypatch, caplog):
    import logging

    # 1. Creamos las carpetas temporales.
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()

    # 2. Preparamos un JSON válido.
    valid_data = {
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

    # 3. Creamos otro JSON con humedad inválida.
    invalid_data = {
        **valid_data,
        "name": "Ciudad inválida",
        "main": {
            **valid_data["main"],
            "humidity": 150,
        },
    }

    # 4. Guardamos los dos JSON en la carpeta temporal.
    (raw_dir / "weather_2026-10-20_10-30-00.json").write_text(
        json.dumps(valid_data),
        encoding="utf-8",
    )

    (raw_dir / "weather_2026-10-20_10-31-00.json").write_text(
        json.dumps(invalid_data),
        encoding="utf-8",
    )

    # 5. Hacemos que la transformación utilice las carpetas temporales.
    monkeypatch.setattr(transform, "raw_dir", raw_dir)
    monkeypatch.setattr(transform, "processed_dir", processed_dir)

    # 6. Capturamos los logs y ejecutamos la transformación.
    with caplog.at_level(logging.WARNING):
        transform.run_transform()

    # 7. Comprobamos que solo se ha guardado el registro válido.
    output_file = processed_dir / "weather.csv"

    with output_file.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["city"] == "Barcelona"

    # 8. Comprobamos que el registro inválido se ha detectado.
    assert "Humedad inválida: 150" in caplog.text

def test_run_transform_raises_error_when_no_json_files_exist(tmp_path, monkeypatch):
    
    # 1. Creamos una carpeta raw vacía
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()

    # 2. Indicamos a transform.py que utilice estas carpetas
    monkeypatch.setattr(transform, "raw_dir", raw_dir)
    monkeypatch.setattr(transform, "processed_dir", processed_dir)

    # 3. Comprobamos que se produce el error esperado
    with pytest.raises(FileNotFoundError):
        transform.run_transform()
    
def test_run_transform_raise_error_when_all_json_files_are_invalid(tmp_path, monkeypatch):
    
    # 1. Creamos carpetas temporales
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()

    # 2. Creamos un JSON sintácticamente correcto pero sin los campos necesarios para transformar los datos
    invalid_data = {
        "name": "Barcelona"
    }

    raw_file = raw_dir / "weather_2026-10-20_10-30-00.json"
    raw_file.write_text(
        json.dumps(invalid_data),
        encoding="utf-8"
    )

    # 3. Redirigimos las rutas a las carpetas temporales.
    monkeypatch.setattr(transform, "raw_dir", raw_dir)
    monkeypatch.setattr(transform, "processed_dir", processed_dir)

    # 4. Comprobamos que se lanza el error esperado.
    with pytest.raises(
        ValueError,
        match="ningún archivo contiene datos válidos",
    ):
        transform.run_transform()

    # 5. Comprobamos que no se ha generado un CSV.
    assert not (processed_dir / "weather.csv").exists()

def test_run_transform_skips_malformed_json(tmp_path, monkeypatch, caplog):
    # 1. Creamos las carpetas temporales
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()

    # 2. Creamos un JSON válido
    valid_data = {
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

    valid_file = raw_dir / "weather_2026-10-20_10-30-00.json"
    valid_file.write_text(
        json.dumps(valid_data),
        encoding="utf-8",
    )

    # 3. Creamos un archivo con JSON mal formado
    invalid_file = raw_dir / "weather_2026-10-20_10-31-00.json"
    invalid_file.write_text(
        '{"name": "Barcelona", "main": ',
        encoding="utf-8",
    )

    # 4. Redirigimos las rutas a las carpetas temporales.
    monkeypatch.setattr(transform, "raw_dir", raw_dir)
    monkeypatch.setattr(transform, "processed_dir", processed_dir)

    # 5. Capturamos las advertencias y ejecutamos la transformación
    with caplog.at_level(logging.WARNING): # caplog es una herramienta de pytest que permite inspeccionar mensajes de logging producidos durante la prueba
        transform.run_transform()

    # 6. Comprobamos que el CSV solo contiene el registro válido.
    output_file = processed_dir / "weather.csv"

    with output_file.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["city"] == "Barcelona"

    # 7. Comprobamos que el JSON incorrecto se ha detectado.
    assert "JSON inválido" in caplog.text
    assert invalid_file.name in caplog.text
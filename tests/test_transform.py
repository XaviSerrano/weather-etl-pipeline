import csv
import json
from datetime import datetime, timezone

import transform

import pytest

import logging

# 1. Test para comprobar que se crea un CSV con datos válidos.
def test_run_transform_creates_csv_with_valid_data(monkeypatch, temp_directories, valid_weather_data):

    # tmp_path proporciona una carpeta para trabajar con archivos sin modificar datos reales
    # monkeypatch permite cambiar temporalmente ciertos valores o comportamientos durante el test

    # 1. Prerparamos carpetas temporales para pruebas
    raw_dir, processed_dir = temp_directories

    # 2. Creamos un JSON de ejemplo ficticio con datos meteorológicos válidos.
    raw_file = raw_dir / "weather_2026-10-20_10-30-00.json"

    weather_data = valid_weather_data

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

# 2. Test para comprobar que se omite un registro con humedad inválida.
@pytest.mark.parametrize(
    "humidity",
    [150, "65", True], # (3 vueltas al mismo test)
    ids=[
        "humidity-out-of-range",
        "humidity-string",
        "humidity-boolean",
    ],
)
def test_run_transform_skips_invalid_humidity(
    monkeypatch, caplog, temp_directories, humidity, valid_weather_data
):
    # 1. Creamos las carpetas temporales.
    raw_dir, processed_dir = temp_directories

    # 2. Preparamos un JSON válido.
    valid_data = valid_weather_data

    # 3. Creamos un JSON con humedad inválida.
    invalid_data = {
        **valid_data,  # Con ** reutilizamos los datos válidos y solo modificamos lo necesario
        "name": "Ciudad inválida",
        "main": {
            **valid_data["main"],
            "humidity": humidity, # 150, "65", True (3 vueltas al mismo test)
        },
    }

    # 4. Guardamos los dos JSON.
    (raw_dir / "weather_2026-10-20_10-30-00.json").write_text(
        json.dumps(valid_data),
        encoding="utf-8",
    )

    (raw_dir / "weather_2026-10-20_10-31-00.json").write_text(
        json.dumps(invalid_data),
        encoding="utf-8",
    )

    # 5. Redirigimos las carpetas a las temporales.
    monkeypatch.setattr(transform, "raw_dir", raw_dir)
    monkeypatch.setattr(transform, "processed_dir", processed_dir)

    # 6. Ejecutamos la transformación y capturamos los logs.
    with caplog.at_level(logging.WARNING):
        transform.run_transform()

    # 7. Comprobamos que solo se ha guardado el registro válido.
    output_file = processed_dir / "weather.csv"

    with output_file.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["city"] == "Barcelona"

    # 8. Comprobamos que el registro inválido se ha detectado.
    assert "Humedad inválida" in caplog.text

# 3. Test para comprobar que se lanza un error cuando no existen archivos JSON.
def test_run_transform_raises_error_when_no_json_files_exist(monkeypatch, temp_directories):
    
    # 1. Creamos una carpeta raw vacía
    raw_dir, processed_dir = temp_directories

    # 2. Indicamos a transform.py que utilice estas carpetas
    monkeypatch.setattr(transform, "raw_dir", raw_dir)
    monkeypatch.setattr(transform, "processed_dir", processed_dir)

    # 3. Comprobamos que se produce el error esperado
    with pytest.raises(FileNotFoundError):
        transform.run_transform()
    
# 4. Test para comprobar que se lanza un error cuando todos los JSON son inválidos.
def test_run_transform_raise_error_when_all_json_files_are_invalid(monkeypatch, temp_directories):
    
    # 1. Creamos carpetas temporales
    raw_dir, processed_dir = temp_directories

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

# 5. Test para comprobar que se omite un JSON malformado.
def test_run_transform_skips_malformed_json(monkeypatch, caplog, temp_directories, valid_weather_data):
    # 1. Creamos las carpetas temporales
    raw_dir, processed_dir = temp_directories

    # 2. Creamos un JSON válido
    valid_data = valid_weather_data

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

# 6. Test para comprobar que se omite un archivo con nombre incorrecto.
def test_run_transform_skips_invalid_filename(monkeypatch, caplog, temp_directories):
    raw_dir, processed_dir = temp_directories

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

    (raw_dir / "weather_2026-10-20_10-30-00.json").write_text(
        json.dumps(valid_data), encoding="utf-8"
    )

    (raw_dir / "weather_fecha_incorrecta.json").write_text(
        json.dumps(valid_data), encoding="utf-8"
    )

    monkeypatch.setattr(transform, "raw_dir", raw_dir)
    monkeypatch.setattr(transform, "processed_dir", processed_dir)

    with caplog.at_level(logging.WARNING):
        transform.run_transform()

    output_file = processed_dir / "weather.csv"

    with output_file.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["city"] == "Barcelona"
    assert "Datos inválidos" in caplog.text

# 7. Test para comprobar que se omite un JSON que no es un diccionario.
def test_run_transform_skips_json_that_is_not_a_dictionary(
    monkeypatch, caplog, temp_directories
):
    raw_dir, processed_dir = temp_directories

    raw_file = raw_dir / "weather_2026-10-20_10-30-00.json"

    raw_file.write_text(
        json.dumps(["Barcelona", "Madrid"]),
        encoding="utf-8",
    )

    monkeypatch.setattr(transform, "raw_dir", raw_dir)
    monkeypatch.setattr(transform, "processed_dir", processed_dir)

    with caplog.at_level(logging.WARNING):
        with pytest.raises(ValueError, match="ningún archivo contiene datos válidos"):
            transform.run_transform()

    assert "El contenido JSON no es un objeto" in caplog.text

# 8. Test para comprobar que se lanza un error cuando no se puede guardar el CSV.
def test_run_transform_raises_error_when_csv_cannot_be_saved(
    monkeypatch, temp_directories
):
    raw_dir, processed_dir = temp_directories

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

    raw_file = raw_dir / "weather_2026-10-20_10-30-00.json"
    raw_file.write_text(json.dumps(valid_data), encoding="utf-8")

    monkeypatch.setattr(transform, "raw_dir", raw_dir)
    monkeypatch.setattr(transform, "processed_dir", processed_dir)

    original_open = open

    def mock_open(file, *args, **kwargs):
        if file == processed_dir / "weather.csv":
            raise OSError("Error simulado al guardar el CSV")

        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(transform, "open", mock_open, raising=False)

    with pytest.raises(OSError, match="Error simulado"):
        transform.run_transform()

#9. Test para comprobar que se crea el directorio de logs si no existe.
def test_configure_logging_creates_logs_directory(tmp_path, monkeypatch):
    logs_dir = tmp_path / "logs"

    monkeypatch.setattr(transform, "logs_dir", logs_dir)

    transform.configure_logging()

    assert logs_dir.exists()
    assert logs_dir.is_dir()

# 10. Test para comprobar que se omite un JSON cuando no se puede leer.
def test_run_transform_skips_unreadable_json(
    monkeypatch, caplog, temp_directories
):
    # 1. Creamos las carpetas temporales.
    raw_dir, processed_dir = temp_directories

    # 2. Preparamos unos datos meteorológicos válidos.
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

    # 3. Creamos los dos archivos JSON.
    unreadable_file = raw_dir / "weather_2026-10-20_10-30-00.json"
    valid_file = raw_dir / "weather_2026-10-20_10-31-00.json"

    unreadable_file.write_text(
        json.dumps(valid_data),
        encoding="utf-8",
    )

    valid_file.write_text(
        json.dumps(valid_data),
        encoding="utf-8",
    )

    # 4. Redirigimos las rutas a las carpetas temporales.
    monkeypatch.setattr(transform, "raw_dir", raw_dir)
    monkeypatch.setattr(transform, "processed_dir", processed_dir)

    # 5. Guardamos la función open original.
    original_open = open

    # 6. Simulamos un error al intentar leer el primer JSON.
    def mock_open(file, *args, **kwargs):
        if file == unreadable_file:
            raise OSError("Error simulado al leer el JSON")

        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(transform, "open", mock_open, raising=False)

    # 7. Ejecutamos la transformación y capturamos los logs.
    with caplog.at_level(logging.ERROR):
        transform.run_transform()

    # 8. Comprobamos que solo se ha procesado el JSON válido.
    output_file = processed_dir / "weather.csv"

    with output_file.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["city"] == "Barcelona"

    # 9. Comprobamos que se ha registrado el error de lectura.
    assert "No se pudo leer" in caplog.text
    assert "Error simulado al leer el JSON" in caplog.text
    assert unreadable_file.name in caplog.text


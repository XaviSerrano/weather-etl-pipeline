
import json
from unittest.mock import Mock

import extract

import pytest

# 1. Test para comrobar que se guarda correctamente la información meteorológica en un archivo JSON.

def test_run_extract_saves_weather_data(tmp_path, monkeypatch):
    # 1. Simulamos una API key.
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-api-key")

    # 2. Redirigimos el directorio del proyecto a una carpeta temporal.
    monkeypatch.setattr(extract, "project_dir", tmp_path)

    # 3. Creamos datos meteorológicos de ejemplo.
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

    # 4. Simulamos la respuesta de OpenWeather.
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = weather_data

    # 5. Simulamos requests.get() para evitar una petición real.
    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr(extract.requests, "get", mock_get)

    # 6. Ejecutamos la extracción.
    extract.run_extract()

    # 7. Comprobamos que se ha realizado la petición correctamente.
    mock_get.assert_called_once_with(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": "Barcelona,ES",
            "appid": "test-api-key",
            "units": "metric",
            "lang": "es",
        },
        timeout=30,
    )

    # 8. Buscamos el archivo JSON generado.
    raw_dir = tmp_path / "data" / "raw"
    json_files = list(raw_dir.glob("weather_*.json"))

    assert len(json_files) == 1

    # 9. Comprobamos que el contenido coincide con los datos recibidos.
    with json_files[0].open("r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == weather_data

# 2. Test para comprobar que se lanza un error cuando falta la API Key.
def test_run_extract_raises_error_when_api_key_is_missing(
    tmp_path,
    monkeypatch,
):
    # 1. Utilizamos un directorio temporal sin archivo .env.
    monkeypatch.setattr(extract, "project_dir", tmp_path)

    # 2. Eliminamos la API Key del entorno.
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)

    # 3. Comprobamos que se lanza la excepción esperada.
    with pytest.raises(
        ValueError,
        match="Falta configurar OPENWEATHER_API_KEY",
    ):
        extract.run_extract()

# 3. Test para comprobar que se lanza un error cuando la API devuelve un error HTTP.
def test_run_extract_raises_error_when_api_returns_http_error(
    tmp_path,
    monkeypatch,
    caplog,
):
    # 1. Configuramos una API Key ficticia.
    monkeypatch.setenv("OPENWEATHER_API_KEY", "invalid-api-key")

    # 2. Redirigimos el proyecto a un directorio temporal.
    monkeypatch.setattr(extract, "project_dir", tmp_path)

    # 3. Simulamos una respuesta HTTP 401.
    mock_response = Mock()
    mock_response.status_code = 401

    # 4. Hacemos que raise_for_status() lance una excepción HTTPError.
    mock_response.raise_for_status.side_effect = (
        extract.requests.exceptions.HTTPError("401 Client Error")
    )

    # 5. Simulamos la petición a OpenWeather.
    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr(extract.requests, "get", mock_get)

    # 6. Comprobamos que se propaga la excepción HTTPError.
    with pytest.raises(extract.requests.exceptions.HTTPError):
        extract.run_extract()

    # 7. Comprobamos que se ha registrado el error.
    assert "Error HTTP de OpenWeather" in caplog.text

    # 8. Comprobamos que se ha realizado una única petición.
    mock_get.assert_called_once()

    # 9. Comprobamos que no se ha guardado ningún JSON.
    raw_dir = tmp_path / "data" / "raw"
    assert not list(raw_dir.glob("weather_*.json"))

# 4. Test para comprobar que se lanza un error cuando la petición HTTP supera el tiempo máximo de espera.
def test_run_extract_raises_error_when_request_times_out(
    tmp_path,
    monkeypatch,
    caplog,
):
    # 1. Configuramos una API Key ficticia.
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-api-key")

    # 2. Redirigimos el proyecto a un directorio temporal.
    monkeypatch.setattr(extract, "project_dir", tmp_path)

    # 3. Simulamos un timeout durante la petición HTTP.
    mock_get = Mock(
        side_effect=extract.requests.exceptions.Timeout(
            "La petición ha superado el tiempo máximo de espera"
        )
    )

    # 4. Sustituimos requests.get() por nuestro Mock.
    monkeypatch.setattr(extract.requests, "get", mock_get)

    # 5. Comprobamos que se propaga la excepción Timeout.
    with pytest.raises(extract.requests.exceptions.Timeout):
        extract.run_extract()

    # 6. Comprobamos que se ha registrado el error.
    assert "Error de conexión o petición a OpenWeather" in caplog.text

    # 7. Comprobamos que se ha realizado una única petición.
    mock_get.assert_called_once()

    # 8. Comprobamos que no se ha generado ningún JSON.
    raw_dir = tmp_path / "data" / "raw"
    assert not list(raw_dir.glob("weather_*.json"))

# 5. Test para comprobar que se lanza un error cuando la respuesta HTTP contiene JSON inválido.
def test_run_extract_raises_error_when_response_is_invalid_json(
    tmp_path,
    monkeypatch,
    caplog,
):
    # 1. Configuramos una API Key ficticia.
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-api-key")

    # 2. Redirigimos el proyecto a un directorio temporal.
    monkeypatch.setattr(extract, "project_dir", tmp_path)

    # 3. Simulamos una respuesta HTTP 200.
    mock_response = Mock()
    mock_response.status_code = 200

    # 4. Hacemos que json() lance un error de decodificación.
    mock_response.json.side_effect = (
        extract.requests.exceptions.JSONDecodeError(
            "Respuesta JSON inválida",
            "contenido no válido",
            0,
        )
    )

    # 5. Simulamos la petición a OpenWeather.
    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr(extract.requests, "get", mock_get)

    # 6. Comprobamos que se propaga la excepción.
    with pytest.raises(extract.requests.exceptions.JSONDecodeError):
        extract.run_extract()

    # 7. Comprobamos que se ha registrado el error.
    assert (
        "La respuesta de OpenWeather no contiene JSON válido"
        in caplog.text
    )

    # 8. Comprobamos que se ha realizado una única petición.
    mock_get.assert_called_once()

    # 9. Comprobamos que no se ha generado ningún JSON.
    raw_dir = tmp_path / "data" / "raw"
    assert not list(raw_dir.glob("weather_*.json"))

# 6. Test para comprobar que se lanza un error cuando no se puede guardar el archivo JSON.
def test_run_extract_raises_error_when_file_cannot_be_saved(
    tmp_path,
    monkeypatch,
    caplog,
):
    # 1. Configuramos una API Key ficticia.
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-api-key")

    # 2. Redirigimos el proyecto a un directorio temporal.
    monkeypatch.setattr(extract, "project_dir", tmp_path)

    # 3. Simulamos datos meteorológicos válidos.
    weather_data = {
        "name": "Barcelona",
        "main": {"temp": 20.5},
    }

    # 4. Simulamos una respuesta correcta de OpenWeather.
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = weather_data

    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr(extract.requests, "get", mock_get)

    # 5. Simulamos un error al intentar abrir el archivo.
    mock_open = Mock(
        side_effect=OSError("Permiso denegado")
    )
    monkeypatch.setattr(extract, "open", mock_open, raising=False)

    # 6. Comprobamos que se propaga la excepción OSError.
    with pytest.raises(OSError, match="Permiso denegado"):
        extract.run_extract()

    # 7. Comprobamos que se ha registrado el error.
    assert "No se pudieron guardar los datos" in caplog.text

    # 8. Comprobamos que se ha realizado la petición.
    mock_get.assert_called_once()

    # 9. Comprobamos que se ha intentado abrir el archivo.
    mock_open.assert_called_once()

    # 10. Comprobamos que no se ha generado ningún JSON.
    raw_dir = tmp_path / "data" / "raw"
    assert not list(raw_dir.glob("weather_*.json"))


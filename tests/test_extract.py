
import json
from unittest.mock import Mock

import extract


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

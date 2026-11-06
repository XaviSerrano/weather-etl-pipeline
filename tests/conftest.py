import sys
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))


@pytest.fixture
def temp_directories(tmp_path):

    """Crea y devuelve las caprpetas temporales de la pipeline"""

    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    
    raw_dir.mkdir()
    processed_dir.mkdir()
    
    return raw_dir, processed_dir


@pytest.fixture
def valid_weather_data():
    """Devuelve un conjunto de datos meteorológicos válidos para las pruebas."""

    return {
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
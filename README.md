# Testing y pruebas automatizadas

## 1. Introducción

Se ha incorporado un sistema de pruebas automatizadas mediante **pytest** al proyecto Weather ETL Pipeline.

El objetivo es verificar el correcto funcionamiento de las fases de extracción y transformación, comprobar la gestión de errores y garantizar la calidad de los datos antes de continuar con el proceso ETL.

Las pruebas utilizan datos simulados y directorios temporales para evitar llamadas innecesarias a servicios externos y modificaciones en los archivos reales del proyecto.

## 2. Tests implementados

### Extract — `tests/test_extract.py`

Pruebas destinadas a verificar el funcionamiento de la extracción de datos desde OpenWeather API.

| Test | Descripción |
|---|---|
| `test_run_extract_saves_weather_data` | Comprueba que los datos recibidos se guardan correctamente en formato JSON. |
| `test_run_extract_raises_error_when_api_key_is_missing` | Verifica que se lanza un error cuando no está configurada la API Key. |
| `test_run_extract_raises_error_when_api_returns_http_error` | Comprueba la gestión de errores HTTP devueltos por la API. |
| `test_run_extract_raises_error_when_request_times_out` | Verifica la gestión de errores por tiempo de espera agotado. |
| `test_run_extract_raises_error_when_response_is_invalid_json` | Comprueba que se detectan respuestas JSON mal formadas. |
| `test_run_extract_raises_error_when_file_cannot_be_saved` | Verifica la gestión de errores al guardar los archivos JSON. |

### Transform — `tests/test_transform.py`

Pruebas destinadas a verificar la lectura, validación y transformación de los archivos JSON en un CSV.

| Test | Descripción |
|---|---|
| `test_run_transform_creates_csv_with_valid_data` | Comprueba la generación correcta del CSV a partir de datos válidos. |
| `test_run_transform_skips_invalid_humidity` | Verifica que se descartan registros con valores de humedad fuera del rango permitido. |
| `test_run_transform_raises_error_when_no_json_files_exist` | Comprueba la gestión de errores cuando no existen archivos JSON para procesar. |
| `test_run_transform_raise_error_when_all_json_files_are_invalid` | Verifica que se lanza un error cuando todos los archivos contienen datos inválidos. |
| `test_run_transform_skips_malformed_json` | Comprueba que se ignoran los archivos JSON mal formados y se procesan los válidos. |

## 3. Herramientas y funcionalidades utilizadas

### Pytest

Framework de testing utilizado para descubrir, ejecutar y verificar las pruebas automatizadas.

### Fixtures de pytest

- **`tmp_path`**: proporciona directorios temporales aislados para cada prueba.
- **`monkeypatch`**: permite modificar temporalmente variables de entorno, atributos y funciones durante las pruebas.
- **`caplog`**: permite capturar y verificar los mensajes generados mediante logging.
- **`pytest.raises()`**: permite comprobar que una función lanza la excepción esperada.

### unittest.mock

Biblioteca estándar de Python utilizada para simular dependencias y servicios externos.

- **`Mock`**: crea objetos simulados para sustituir funciones o servicios reales.
- **`return_value`**: define el resultado devuelto por un objeto simulado.
- **`side_effect`**: permite simular excepciones y comportamientos alternativos.
- **`assert_called_once()`**: comprueba que una función se ha ejecutado exactamente una vez.
- **`assert_called_once_with()`**: comprueba que una función se ha ejecutado una vez con los argumentos esperados.

## 4. Dependencias

La principal dependencia incorporada para implementar las pruebas automatizadas es:

| Dependencia | Descripción |
|---|---|
| `pytest` | Framework para ejecutar y gestionar las pruebas automatizadas. |

También se utilizan funcionalidades incluidas en Python o integradas en pytest, por lo que no requieren instalaciones adicionales:

- `unittest.mock`
- `tmp_path`
- `monkeypatch`
- `caplog`
- `pathlib`
- `json`

## 5. Ejecución de las pruebas

Para ejecutar toda la batería de tests desde el directorio raíz del proyecto:

- `pytest`: ejecuta todas las pruebas.
- `pytest -v`: ejecuta las pruebas mostrando el nombre y resultado de cada una.
- `pytest tests/test_extract.py`: ejecuta únicamente las pruebas de extracción.
- `pytest tests/test_transform.py`: ejecuta únicamente las pruebas de transformación.

## 6. Objetivos alcanzados

La incorporación de estas pruebas permite:

- Verificar el funcionamiento de las fases de extracción y transformación.
- Detectar errores de conexión y respuestas incorrectas de servicios externos.
- Comprobar la gestión de excepciones.
- Validar la calidad e integridad de los datos.
- Evitar modificaciones en los archivos reales durante las pruebas.
- Reducir la dependencia de servicios externos durante el desarrollo.
- Facilitar el mantenimiento y futuras ampliaciones de la pipeline.

## 7. Próximos pasos

- Implementar pruebas automatizadas para la fase de carga (`load.py`).
- Implementar pruebas para la orquestación de la pipeline (`main.py`).
- Ampliar las validaciones de calidad de datos.
- Integrar la ejecución de los tests en un flujo de integración continua (CI/CD).
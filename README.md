# Testing y pruebas automatizadas

## 1. Introducción

Se ha incorporado un sistema de pruebas automatizadas mediante **pytest** al proyecto Weather ETL Pipeline.

El objetivo es verificar el correcto funcionamiento de las tres fases del proceso ETL (extracción, transformación y carga), comprobar la gestión de errores, validar la integridad de los datos y garantizar que la orquestación de la pipeline funciona correctamente.

Las pruebas utilizan datos simulados (*mocking*), variables de entorno controladas y directorios temporales para evitar llamadas innecesarias a servicios externos y modificaciones en los archivos reales del proyecto.

Actualmente, el proyecto cuenta con **20 pruebas automatizadas**, todas ejecutadas correctamente.

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

**Total: 6 tests.**

### Transform — `tests/test_transform.py`

Pruebas destinadas a verificar la lectura, validación y transformación de los archivos JSON en un CSV.

| Test | Descripción |
|---|---|
| `test_run_transform_creates_csv_with_valid_data` | Comprueba la generación correcta del CSV a partir de datos válidos. |
| `test_run_transform_skips_invalid_humidity` | Verifica que se descartan registros con valores de humedad fuera del rango permitido. |
| `test_run_transform_raises_error_when_no_json_files_exist` | Comprueba la gestión de errores cuando no existen archivos JSON para procesar. |
| `test_run_transform_raise_error_when_all_json_files_are_invalid` | Verifica que se lanza un error cuando todos los archivos contienen datos inválidos. |
| `test_run_transform_skips_malformed_json` | Comprueba que se ignoran los archivos JSON mal formados y se procesan los válidos. |

**Total: 5 tests.**

### Load — `tests/test_load.py`

Pruebas destinadas a verificar la carga de los datos del CSV en PostgreSQL, incluyendo las validaciones previas y la gestión de errores.

| Test | Descripción |
|---|---|
| `test_run_load_inserts_weather_data` | Comprueba que los registros del CSV se insertan correctamente en PostgreSQL. |
| `test_run_load_raises_error_when_database_connection_fails` | Verifica la gestión de errores cuando no se puede establecer la conexión con PostgreSQL. |
| `test_run_load_raises_error_when_csv_does_not_exist` | Comprueba que se lanza un error cuando no existe el archivo CSV. |
| `test_run_load_raises_error_when_csv_headers_are_invalid` | Verifica que se detectan las cabeceras obligatorias ausentes en el CSV. |
| `test_run_load_raises_error_when_required_values_are_empty` | Comprueba que se rechazan registros con campos obligatorios vacíos. |

**Total: 5 tests.**

### Main — `tests/test_main.py`

Pruebas destinadas a verificar la correcta orquestación de las tres fases de la pipeline ETL.

| Test | Descripción |
|---|---|
| `test_main_executes_pipeline_in_correct_order` | Comprueba que las fases de extracción, transformación y carga se ejecutan en el orden correcto. |
| `test_main_stops_when_extraction_fails` | Verifica que un error durante la extracción detiene la pipeline e impide ejecutar las fases posteriores. |
| `test_main_stops_when_transformation_fails` | Comprueba que un error durante la transformación impide ejecutar la fase de carga. |
| `test_main_logs_success_message` | Verifica que se registra el mensaje de finalización correcta cuando todas las fases terminan sin errores. |

**Total: 4 tests.**

## 3. Resumen de cobertura de pruebas

| Módulo | Tests implementados |
|---|---:|
| Extract | 6 |
| Transform | 5 |
| Load | 5 |
| Main | 4 |
| **Total** | **20** |

**Última ejecución:**

- Tests recopilados: 20.
- Tests superados: 20.
- Tests fallidos: 0.
- Tiempo de ejecución: 0,49 segundos.

## 4. Herramientas y funcionalidades utilizadas

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
- **`MagicMock`**: permite simular objetos que implementan métodos especiales y comportamientos más complejos.
- **`return_value`**: define el resultado devuelto por un objeto simulado.
- **`side_effect`**: permite simular excepciones y comportamientos alternativos.
- **`assert_called_once()`**: comprueba que una función se ha ejecutado exactamente una vez.
- **`assert_called_once_with()`**: comprueba que una función se ha ejecutado una vez con los argumentos esperados.
- **`assert_not_called()`**: comprueba que una función no ha llegado a ejecutarse.

## 5. Dependencias

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
- `logging`

## 6. Ejecución de las pruebas

Para ejecutar toda la batería de tests desde el directorio raíz del proyecto:

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar mostrando el nombre y resultado de cada test
pytest -v

# Ejecutar únicamente las pruebas de extracción
pytest tests/test_extract.py

# Ejecutar únicamente las pruebas de transformación
pytest tests/test_transform.py

# Ejecutar únicamente las pruebas de carga
pytest tests/test_load.py

# Ejecutar únicamente las pruebas de orquestación
pytest tests/test_main.py
```

## 7. Objetivos alcanzados

La incorporación de estas pruebas permite:

- Verificar el funcionamiento de las tres fases principales del proceso ETL.
- Comprobar la correcta secuencia de ejecución de la pipeline.
- Detectar errores de conexión y respuestas incorrectas de servicios externos.
- Comprobar la gestión de excepciones y los mecanismos de recuperación ante fallos.
- Validar la calidad e integridad de los datos.
- Verificar que los registros obligatorios contienen valores válidos antes de su inserción.
- Comprobar que se gestionan correctamente los registros duplicados.
- Evitar modificaciones en los archivos reales durante las pruebas que utilizan directorios temporales.
- Reducir la dependencia de servicios externos durante el desarrollo.
- Facilitar el mantenimiento y futuras ampliaciones de la pipeline.

## 8. Próximos pasos

- Incorporar `pytest-cov` para medir la cobertura del código y detectar partes que todavía no están cubiertas por las pruebas.
- Ampliar los casos de prueba para contemplar situaciones límite y posibles errores adicionales.
- Mejorar la documentación técnica del proyecto.
- Integrar la ejecución automática de los tests mediante un flujo de integración continua (CI/CD), por ejemplo, GitHub Actions.
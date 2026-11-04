import load
import pytest

from unittest.mock import MagicMock, Mock

# 1. Probamos la función run_load para insertar datos meteorológicos en PostgreSQL.
def test_run_load_inserts_weather_data(tmp_path, monkeypatch):
    
    # 1. Configuramos variables de conexión ficticias.
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")

    # 2. Creamos un CSV temporal con un registro válido.
    csv_content = (
        "extracted_at,city,country,temperature_c,feels_like_c,"
        "humidity_pct,pressure_hpa,weather_description,"
        "wind_speed_m_s,cloudiness_pct,observed_at_utc\n"
        "2026-11-03 10:00:00,Barcelona,ES,20.5,19.8,"
        "65,1015,Cielo despejado,3.5,10,2026-11-03 09:00:00\n"
    )

    test_csv = tmp_path / "weather.csv"
    test_csv.write_text(csv_content, encoding="utf-8")

    monkeypatch.setattr(load, "csv_file", test_csv)

    # 3. Simulamos el cursor de PostgreSQL.
    mock_cursor = Mock()
    mock_cursor.rowcount = 1

    # 4. Simulamos la conexión.
    mock_connection = MagicMock()
    mock_connection.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = (
        mock_cursor
    )

    # 5. Sustituimos la conexión real por nuestra conexión simulada.
    mock_connect = Mock(return_value=mock_connection)
    monkeypatch.setattr(load.psycopg2, "connect", mock_connect)

    # 6. Ejecutamos la función que queremos probar.
    load.run_load()

    # 7. Comprobamos que se ha establecido la conexión.
    mock_connect.assert_called_once_with(
        host="localhost",
        port="5432",
        dbname="test_db",
        user="test_user",
        password="test_password",
    )

    # 8. Comprobamos que se ha ejecutado una inserción.
    mock_cursor.execute.assert_called_once()

    # 9. Comprobamos que la conexión se ha cerrado.
    mock_connection.close.assert_called_once()

# 2. Probamos que se lanza un error cuando la conexión a la base de datos falla.
def test_run_load_raises_error_when_database_connection_fails(
    tmp_path, monkeypatch
):

    # 1. Configuramos variables de entorno ficticias
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")

    # 2. Creamos un CSV temporal
    csv_file = tmp_path / "weather.csv"
    csv_file.write_text(
        "extracted_at,city,country\n"
        "2026-11-04 10:00:00,Barcelona,ES\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(load, "csv_file", csv_file)

    # 3. Simulamos un error al conectar con PostgreSQL
    monkeypatch.setattr(
        load.psycopg2, # librería psycopg2 dentro de nuestro load.py que vamos a modificar
        "connect", # nombre del atributo que vamos a modificar
        Mock(side_effect=load.psycopg2.OperationalError)
    )

    # 4. Comprobamos que el error se lanza correctamente
    with pytest.raises(load.psycopg2.OperationalError):
        load.run_load()

# 3. Probamos que se lanza un error cuando el CSV no existe.
def test_run_load_raises_error_when_csv_does_not_exist(
    tmp_path, monkeypatch
):
    # 1. Creamos una ruta a un CSV que no existe
    csv_file = tmp_path / "weather.csv"

    # 2. Sustituimos la ruta original por nuestra ruta temporal
    monkeypatch.setattr(load, "csv_file", csv_file)

    # 3. Comprobamos que se lanza FileNotFoundError
    with pytest.raises(FileNotFoundError):
        load.run_load()

# 4. Probamos que se lanza un error cuando las cabeceras del CSV son inválidas.
def test_run_load_raises_error_when_csv_headers_are_invalid(
    tmp_path, monkeypatch
):

    # 1. Creamos un CSV con cabeceras incorrectas
    csv_file = tmp_path / "weather.csv"

    csv_file.write_text(
        "date,location,temperature\n"
        "2026-11-04,Barcelona,18.5\n",
        encoding="utf-8"
    )

    # 2. Sustituimos la ruta original del CSV
    monkeypatch.setattr(load, "csv_file", csv_file)

    # 3. Configuramos variables de entorno ficticias
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")

    # 5. Comprobamos que se lanza ValueError
    with pytest.raises(ValueError):
        load.run_load()


# 5. Probamos que se lanza un error cuando los valores obligatorios están vacíos en el CSV.
def test_run_load_raises_error_when_required_values_are_empty(
    tmp_path, monkeypatch
):

    # 1. Creamos un CSV con valores obligatorios vacíos
    csv_file = tmp_path / "weather.csv"

    csv_file.write_text(
        "extracted_at,city,country\n"
        ",Barcelona,ES\n",
        encoding="utf-8"
    )

    # 2. Sustituimos la ruta original del CSV
    monkeypatch.setattr(load, "csv_file", csv_file)

    # 3. Configuramos variables de entorno ficticias
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")

    # 4. Comprobamos que se lanza ValueError
    with pytest.raises(ValueError):
        load.run_load()
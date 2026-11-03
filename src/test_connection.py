import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
env_file = project_dir / ".env"

print("Archivo .env encontrado:", env_file.exists())

# Forzamos la carga de los valores del .env
load_dotenv(env_file, override=True)

password = os.getenv("DB_PASSWORD")

print("Contraseña cargada:", password is not None)
print("Longitud:", len(password) if password else 0)

try:
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=password,
        connect_timeout=5,
    )

    print("¡Conexión establecida correctamente!")
    connection.close()

except Exception as error:
    print("Tipo de error:", type(error).__name__)
    print("Mensaje:", repr(error))
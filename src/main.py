
import logging
import sys
from datetime import datetime
from pathlib import Path

from extract import run_extract
from transform import run_transform
from load import run_load


project_dir = Path(__file__).resolve().parent.parent
logs_dir = project_dir / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)


def configure_logging():
    """Configura el registro global de la pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                logs_dir / "main.log",
                encoding="utf-8",
            ),
        ],
        force=True,
    )


def main():
    start_time = datetime.now()

    logging.info("========== INICIO DE LA PIPELINE ETL ==========")

    try:
        logging.info("FASE 1/3: Extracción")
        run_extract()

        logging.info("FASE 2/3: Transformación")
        run_transform()

        logging.info("FASE 3/3: Carga en PostgreSQL")
        run_load()

    except Exception:
        logging.exception("La pipeline ETL ha fallado")
        sys.exit(1)

    elapsed = (datetime.now() - start_time).total_seconds()

    logging.info(
        "PIPELINE FINALIZADA CORRECTAMENTE en %.2f segundos",
        elapsed,
    )


if __name__ == "__main__":
    configure_logging()
    main()

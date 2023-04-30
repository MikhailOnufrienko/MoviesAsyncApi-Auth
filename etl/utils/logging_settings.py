import logging
import os

from dotenv import load_dotenv

load_dotenv()

LOGLEVEL = os.getenv('LOGLEVEL').upper()


def setup_logging() -> None:
    """Конфигурация для логирования."""

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=LOGLEVEL,
        datefmt='%d-%b-%y %H:%M',
    )

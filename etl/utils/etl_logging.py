import logging

from src.core import config


logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(
    config.BASE_DIR / 'etl/information.log', mode='w'
)

file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s %(message)s'
)

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

logger.info("Logger initialized")

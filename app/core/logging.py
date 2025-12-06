from loguru import logger
import sys
from .config import get_settings


def setup_logging() -> None:
    settings = get_settings()
    logger.remove()
    logger.add(
        sys.stdout,
        level="DEBUG" if settings.environment == "local" else "INFO",
        format="<green>{time}</green> | <level>{level}</level> | {message}",
    )

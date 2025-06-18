from dataclasses import field
from typing import Final

from pydantic import BaseModel
from logging.config import dictConfig


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: Final[str] = "uvicorn"
    LOG_FORMAT: Final[str] = "%(levelname)s [%(asctime)s] %(message)s"
    LOG_LEVEL: Final[str] = "INFO"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict[str, dict[str, str]] = field(default_factory=lambda: {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LogConfig.LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    })
    handlers: dict[str, dict[str, str]] = field(default_factory=lambda: {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    })
    loggers: dict[str, dict[str, str]] = field(default_factory=lambda: {
        LogConfig.LOGGER_NAME: {"handlers": ["default"], "level": LogConfig.LOG_LEVEL},
    })


dictConfig(LogConfig().model_dump())

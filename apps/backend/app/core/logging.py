"""Structured logging configuration using structlog.

Provides JSON logs in production and coloured console output in
development, with consistent processors for timestamps, log levels,
and call-site information.
"""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(environment: str, log_level: str) -> None:
    """Set up structlog and stdlib logging for the entire application.

    Args:
        environment: Runtime environment name (``development`` | ``production``).
        log_level: Python log-level name (``DEBUG``, ``INFO``, etc.).
    """
    log_level_upper: str = log_level.upper()
    numeric_level: int = getattr(logging, log_level_upper, logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if environment == "production":
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(numeric_level)

    # Quieten noisy third-party loggers
    for noisy in ("uvicorn", "uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger for the given module name.

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        structlog.stdlib.BoundLogger: A logger bound with the module name.
    """
    return structlog.get_logger(name)

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from codeborn_shared.config import LoggingConfig


def init_logging(config: LoggingConfig) -> None:
    """Initialize logging configuration."""
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt='%Y-%m-%dT%H:%M:%S.%fZ', utc=True),
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(config.level),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True
    )


def get_logger(**kwargs) -> structlog.BoundLogger:
    """Get a logger instance."""
    return structlog.get_logger().bind(**kwargs)

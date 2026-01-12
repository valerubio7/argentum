"""Structured logging configuration."""

import logging
import sys

import structlog


def add_request_id(logger, method_name, event_dict):
    """Add request ID to log events if available.

    Args:
        logger: Logger instance
        method_name: Name of the method being called
        event_dict: Event dictionary

    Returns:
        Event dictionary with request_id added if available
    """
    from presentation.api.middleware.request_id import get_request_id

    request_id = get_request_id()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def setup_logging(environment: str = "development", log_level: str = "INFO") -> None:
    """Configure structured logging with structlog.

    Args:
        environment: Environment name (development, production, test)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Determine if we should use JSON format (production) or console format (development)
    use_json = environment.lower() == "production"

    # Configure structlog processors
    processors = [
        # Add log level
        structlog.stdlib.add_log_level,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Add request ID from context
        add_request_id,
        # Add caller info (file, function, line)
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ],
        ),
        # Stack unwinder for exceptions
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        # Format exception
        structlog.processors.format_exc_info,
    ]

    if use_json:
        # Production: JSON output
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Human-readable colored output
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            )
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)

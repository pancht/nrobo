import logging
import os
import sys

from colorlog import ColoredFormatter

from nrobo.core import settings
from nrobo.helpers.logging_extensions import configure_logging
from nrobo.helpers.nrobo_helper import has_dev_flag
from nrobo.helpers.typing_logging import DevLogger


def get_logger(
    name: str,
    log_level_stream: str = settings.LOG_LEVEL_STREAM,
    log_level_file: str = settings.LOG_LEVEL_FILE,
) -> DevLogger:
    log_dir = os.path.join(settings.LOG_DIR)  # noqa: E501
    os.makedirs(log_dir, exist_ok=True)

    unique_logger_name = f"{settings.NROBO_APP}.log"
    log_path = os.path.join(log_dir, unique_logger_name)

    # Initialize logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEV_DEBUG if has_dev_flag() else logging.DEBUG)

    # Avoid duplicate handlers (important in pytest runs)
    if logger.handlers:
        return logger

    # Stream handler (stdout)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEV_DEBUG if has_dev_flag() else log_level_stream)
    ch.setFormatter(
        ColoredFormatter(
            settings.LOG_FORMAT_STREAM,
            log_colors=settings.LOG_COLORS_STREAM,
        )
    )

    # File handler (persistent logs)
    fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    fh.setLevel(logging.DEV_DEBUG if has_dev_flag() else log_level_file)
    fh.setFormatter(logging.Formatter(settings.LOG_FORMAT_FILE))

    # Add handlers
    logger.addHandler(ch)
    logger.addHandler(fh)

    # CRITICAL FIX: prevent root logger from duplicating messages
    # logger.propagate = False
    configure_logging(logger)

    return logger


def set_logger_level(
    logger: logging.Logger, stream_level: int = None, file_level: int = None
):  # noqa: E501
    """
    Dynamically update the log level of the given logger's handlers.

    Args:
        logger: The logger object (e.g. from get_logger()).
        stream_level: Optional new level for stream handler.
        file_level: Optional new level for file handler.
    """
    for handler in logger.handlers:
        # Identify handler type
        if isinstance(handler, logging.StreamHandler) and not isinstance(
            handler, logging.FileHandler
        ):
            if stream_level:  # pragma: no cover
                handler.setLevel(stream_level)
        elif isinstance(handler, logging.FileHandler):  # pragma: no cover
            if file_level:  # pragma: no cover
                handler.setLevel(file_level)

    # Optionally adjust the logger's own level as well
    highest_level = min(
        h.level for h in logger.handlers
    )  # ensures logger accepts lower levels # noqa: E501
    logger.setLevel(highest_level)

# nrobo/helpers/custom_logging.py
import logging

from nrobo.core import settings

DEV_DEBUG = 5

# Register level name
logging.addLevelName(DEV_DEBUG, "DEV_DEBUG")

if not hasattr(logging, "DEV_DEBUG"):  # pragma: no cover
    logging.DEV_DEBUG = DEV_DEBUG


def dev_debug(self, message, *args, **kwargs):
    if self.isEnabledFor(DEV_DEBUG):
        self._log(DEV_DEBUG, message, args, **kwargs)


# Register logger method once
if not hasattr(logging.Logger, "dev_debug"):  # pragma: no cover
    logging.Logger.dev_debug = dev_debug


def configure_logging(logger: logging.Logger):
    """
    Apply correct logger level based on runtime flags.
    """
    if settings.NROBO_DEV_DEBUG:
        logger.setLevel(logging.DEV_DEBUG)
    elif settings.DEBUG:
        logger.setLevel(logging.DEBUG)  # pragma: no cover
    else:
        logger.setLevel(logging.INFO)

from pathlib import Path

from nrobo.core import settings
from nrobo.exceptions import SuiteNotFoundError
from nrobo.helpers.logging import get_logger

logger = get_logger(name=settings.APP)


def validate_suite_files(suites: list[str] | str | None = None):
    for suite in suites or []:
        suite_path = Path(settings.SUITES_DIR) / suite
        if not suite_path.exists():
            raise SuiteNotFoundError(suite_path)

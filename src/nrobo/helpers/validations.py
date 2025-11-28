from pathlib import Path

from nrobo.core import settings
from nrobo.core.exceptions import SuiteNotFoundError


def validate_suite_paths(
    suites: list[str] | str | None = None,
) -> None | SuiteNotFoundError:  # noqa: E501
    """
    Validate that all specified suite files exist in the configured SUITES_DIR.
    Raises SuiteNotFoundError if any file is missing.
    """
    for suite in suites or []:
        suite_path = Path(settings.SUITES_DIR) / suite
        if not suite_path.exists():
            raise SuiteNotFoundError(suite_path)

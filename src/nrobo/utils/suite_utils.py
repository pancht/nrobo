from pathlib import Path

from nrobo.core import settings
from nrobo.core.exceptions import NoTestsFoundException
from nrobo.helpers.logging_helper import get_logger
from nrobo.helpers.validations import validate_suite_paths
from nrobo.utils.common_utils import deduplicate_preserve_order
from nrobo.utils.tests_discovery_utils import has_pytest_tests

logger = get_logger(name=settings.NROBO_APP)


def detect_or_validate_suites(
    suites: list[str] | None = None,
) -> list[str] | None:  # noqa: E501
    """
    Auto-detect available suite files if none are provided.
    Otherwise, validate the given suite list.
    Returns a normalized list of suites or [None] to indicate all tests.

    Raises:
        NoTestsFoundException: If no tests found in "tests" dir.
        SuiteNotFoundError: If no suites found.
    """
    if suites is None:
        suites_dir = Path(settings.SUITES_DIR).resolve()
        yml_files = list(suites_dir.glob("*.yml"))

        if yml_files:
            logger.info(
                f"Auto-detected {len(yml_files)} suite file(s) under {suites_dir}"  # noqa: E501
            )  # noqa: E501
            suites = (
                None  # meaning: run all detected suites (logic continues elsewhere) # noqa: E501
            )
        else:
            logger.debug("⚠️ No suite specified and no suite files found!")
            if not has_pytest_tests(settings.TESTS_DIR):  # noqa: E501
                raise NoTestsFoundException(search_path=settings.TESTS_DIR)
            suites = None
    else:
        validate_suite_paths(suites=suites)

    return deduplicate_preserve_order(suites)

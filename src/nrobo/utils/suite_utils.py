import sys
from pathlib import Path

from nrobo.core import settings
from nrobo.helpers.logging import get_logger
from nrobo.helpers.validations import validate_suite_paths
from nrobo.utils.common_utils import deduplicate_preserve_order
from nrobo.utils.tests_discovery_utils import has_pytest_tests

logger = get_logger(name=settings.APP)


def detect_or_validate_suites(
    suites: list[str] | str | None = None,
) -> list[str] | str | None:  # noqa: E501
    """
    Auto-detect available suite files if none are provided.
    Otherwise, validate the given suite list.
    Returns a normalized list of suites or [None] to indicate all tests.
    """
    if suites is None:
        suites_dir = Path.cwd() / settings.SUITES_DIR
        yml_files = list(suites_dir.glob("*.yml"))

        if yml_files:
            logger.info(
                f"Auto-detected {len(yml_files)} suite file(s) under {suites_dir}"  # noqa: E501
            )  # noqa: E501
            suites = (
                None  # meaning: run all detected suites (logic continues elsewhere) # noqa: E501
            )
        else:
            logger.warning("⚠️ No suite specified and no suite files found!")
            if not has_pytest_tests(settings.TESTS_DIR):
                logger.critical("❌ No pytest tests found in the tests/ directory.")  # noqa: E501
                sys.exit(1)
            suites = None
    else:
        validate_suite_paths(suites=suites)

    return deduplicate_preserve_order(suites)

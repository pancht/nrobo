import sys
from pathlib import Path

import pytest

from nrobo.core import settings
from nrobo.helpers.logging import get_logger
from nrobo.helpers.reporting_helper import generate_allure_report
from nrobo.utils.suite_utils import detect_or_validate_suites

from .helpers._pytest_helper import (
    detect_fixture_usage,
    no_execution_key_found,
    should_proceed,
)
from .runner import prepare_pytest_cli_options

logger = get_logger(name=settings.APP)


def run() -> int:
    # Handle circular import error
    from nrobo.helpers.cli_parser import get_nrobo_arg_parser

    """Main orchestration logic for nRoBo test execution."""
    suites, browser, args, pytest_args = get_nrobo_arg_parser()

    suites = detect_or_validate_suites(suites=suites)
    is_ui_test = detect_fixture_usage("nrobo", [settings.TESTS_DIR], pytest_args=pytest_args)

    # Execution banner
    if is_ui_test:
        mode = "headed" if args.no_headless else "headless"
        logger.info(f"🚀 Starting {settings.APP} test execution on browser: {browser} ({mode})")
    else:
        logger.info("🧪 Running non-browser tests...")

    logger.info(f"🗂 Suites to execute: {suites}")
    logger.debug(f"Pytest args received: {pytest_args}")

    pytest_options = prepare_pytest_cli_options(suites=suites, pytest_args=pytest_args)
    logger.debug(f"Final Pytest CLI options: {pytest_options}")

    try:
        exit_code = pytest.main(args=pytest_options)
    except Exception as e:
        logger.exception(f"❌ Exception occurred during test execution: {e}")
        return 2  # distinct non-success code for internal failure

    if should_proceed(exit_code):
        logger.info("✅ All suites/tests executed successfully.")

    # Skip further reporting if test run was not successful or not valid
    if not should_proceed(exit_code) or no_execution_key_found(pytest_options):
        logger.debug("Skipping report generation due to failed execution or missing keys.")
        return 0

    # Generate Allure report only if allure results exist
    allure_dir = Path(settings.ALLURE_RESULTS_DIR)
    if allure_dir.exists() and any(allure_dir.iterdir()):
        generate_allure_report()
    else:
        logger.warning("⚠️ Skipping Allure report — no results found.")

    # Handle coverage report path if requested
    if getattr(args, "cov", False):
        coverage_path = Path("htmlcov/index.html")
        if coverage_path.exists():
            logger.info(f"📈 Coverage report available → file://{coverage_path.resolve()}")
        else:
            logger.warning("⚠️ Coverage report path not found (htmlcov/index.html).")

    return 0


def main() -> None:
    """CLI entrypoint wrapper for nRoBo."""
    exit_status = run()
    sys.exit(exit_status)


if __name__ == "__main__":
    main()

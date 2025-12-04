import sys
from pathlib import Path

import coverage
import pytest

from nrobo.core import settings
from nrobo.core.constants import ExitCodes
from nrobo.core.exceptions import NoTestsFoundException, NRoboError
from nrobo.helpers._pytest_helper import (
    detect_fixture_usage,
    no_execution_key_found,
    prepare_pytest_cli_options,
    should_proceed,
)
from nrobo.helpers.cli_parser import check_if_nrobo_initialized
from nrobo.helpers.logging_helper import get_logger
from nrobo.helpers.reporting_helper import generate_allure_report
from nrobo.utils.suite_utils import detect_or_validate_suites

logger = get_logger(name=settings.NROBO_APP)


def run() -> int:
    check_if_nrobo_initialized()
    # Handle circular import error
    from nrobo.helpers.cli_parser import get_nrobo_arg_parser

    """Main orchestration logic for nRoBo test execution."""
    suites, browser, args, pytest_args = get_nrobo_arg_parser()

    try:
        suites = detect_or_validate_suites(suites=suites)
    except NoTestsFoundException:
        suites = None

    try:
        is_ui_test = detect_fixture_usage(
            "nrobo", [str(settings.TESTS_DIR)], pytest_args=pytest_args
        )
    except NoTestsFoundException as e:
        return e.return_code

    # Execution banner
    if is_ui_test:
        mode = "headed" if args.no_headless else "headless"
        logger.info(
            f"🚀 Starting {settings.NROBO_APP} test execution on browser: {browser} ({mode})"
        )
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
        return pytest.ExitCode.INTERNAL_ERROR  # distinct non-success code for internal failure

    if should_proceed(exit_code) and not no_execution_key_found(pytest_options):
        logger.info("✅ All suites/tests executed successfully.")

    # Skip further reporting if test run was not successful or not valid
    if no_execution_key_found(pytest_options):
        logger.warning(
            "⚠️ Skipped report generation:\n"
            "   • Required execution keys were not found in the pytest options.\n"
            "   • This may happen if options like '--collect-only' were used, which prevent test execution."
        )
        return ExitCodes.SUCCESS

    # Generate Allure report only if allure results exist
    allure_dir = Path(settings.ALLURE_RESULTS_DIR)
    if allure_dir.exists() and any(allure_dir.iterdir()):
        generate_allure_report()
    else:
        logger.warning("⚠️ Skipping Allure report — no results found.")

    # Handle coverage report path if requested
    if getattr(args, "coverage", False):
        try:
            cov = coverage.Coverage()
            cov.combine()
            cov.save()
            logger.info("🧪 Combined coverage data from multiple subprocesses.")
        except Exception as e:
            logger.warning(f"⚠️ Failed to combine coverage data: {e}")

        coverage_path = settings.COVERAGE_REPORT_HTML

        if coverage_path.exists():
            logger.info(f"📈 Coverage report available → file://{coverage_path.resolve()}")
        else:
            logger.warning(
                f"⚠️ Coverage report path not found ({str(settings.COVERAGE_REPORT_HTML)})."
            )

    return 0


def main() -> None:
    """CLI entrypoint wrapper for nRoBo."""
    try:
        exit_code = run()
        sys.exit(exit_code)

    except NRoboError as e:
        logger.error(str(e))
        sys.exit(e.return_code)

    except KeyboardInterrupt:
        logger.warning("❌ Execution interrupted by user.")
        sys.exit(ExitCodes.INTERRUPTED)  # Conventional SIGINT exit code

    except Exception as e:
        logger.exception(f"Unexpected internal error: {e}")
        sys.exit(ExitCodes.INTERNAL_ERROR)  # Generic fatal error


if __name__ == "__main__":
    main()

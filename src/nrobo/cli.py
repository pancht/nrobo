import os

import pytest

from nrobo.core import settings
from nrobo.helpers.cli_parser import get_nrobo_arg_parser
from nrobo.helpers.logging import get_logger
from nrobo.helpers.reporting_helper import (
    generate_allure_report,
    prepare_reporting_args,
)
from nrobo.utils.suite_utils import detect_or_validate_suites

from .helpers._pytest import no_execution_key_found, should_proceed
from .runner import prepare_pytest_cli_options

logger = get_logger(name=settings.APP)


def main():
    suites, browser, args, pytest_args = get_nrobo_arg_parser()

    suites = detect_or_validate_suites(suites=suites)

    msg = "" if args.no_headless else "in headless mode"
    logger.info(f"Starting {settings.APP} test execution on browser: {browser} {msg}")  # noqa: E501
    logger.info(f"Suites to execute: {suites}")
    logger.debug(f"PyTest args: {pytest_args}")

    if args.cov:
        pytest_args.extend(
            [
                "--cov=nrobo",  # measure coverage for your framework package
                "--cov-report=html",  # generate HTML report
                "--cov-report=term-missing",  # show missing lines in terminal
                "--cov-fail-under=90",  # fail if coverage < 90%
            ]
        )

    pytest_args = prepare_reporting_args(pytest_args=pytest_args)

    pytest_options = prepare_pytest_cli_options(
        suites=suites, pytest_args=pytest_args
    )  # noqa: E501
    logger.debug(f"Final PyTest CLI: {pytest_options}")

    exit_code = pytest.main(args=pytest_options)

    logger.info("\n✅ All suites executed successfully.")

    if not should_proceed(exit_code) or no_execution_key_found(pytest_options):
        # no need to proceed further...
        return 0

    generate_allure_report()

    if args.cov:
        logger.info(
            f"📈Open coverage report → file://{os.path.abspath("htmlcov/index.html")}"  # noqa: E501
        )  # noqa: E501


if __name__ == "__main__":
    main()

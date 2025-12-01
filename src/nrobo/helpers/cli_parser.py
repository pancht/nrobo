import argparse
import os
import sys

import pytest

from nrobo.core import settings
from nrobo.helpers.io_helper import copy_configs_if_updated
from nrobo.helpers.logging_helper import get_logger, set_logger_level
from nrobo.helpers.reporting_helper import prepare_reporting_args
from nrobo.utils.command_utils import initialize_project

logger = get_logger(name=settings.NROBO_APP)


def get_nrobo_arg_parser():
    parser = argparse.ArgumentParser(
        description=f"{settings.NROBO_APP} - Smart Test Runner built on Pytest",
        add_help=True,
        allow_abbrev=False,  # ⛔ Prevents "--co" from resolving to "--cov"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode (prints verbose logs and sets NROBO_DEBUG=True)",  # noqa: E501
    )

    # known args
    parser.add_argument(
        "--suite",
        nargs="+",  # Accepts multiple values (space-separated)
        help="One or more suite YAML files under suites/ (space-separated or repeated).",  # noqa: E501
        default=None,
    )  # noqa: E501
    parser.add_argument(
        "--browser",
        action="store",
        help="Browser to run tests on (chrome, firefox, edge, etc.)",
        default=settings.DEFAULT_BROWSER,
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        default=False,
        help="Run browser in headed mode (default is headless)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help=f"Initialize a new {settings.NROBO_APP} project with sample suite and tests.",  # noqa: E501
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        default=False,
        help="Enable coverage reporting for the nRoBo framework. Used for nRobo framework coverage report!",  # noqa: E501
    )

    if "--help" in sys.argv:
        logger.info(f"\n📜 {settings.NROBO_APP} Help Menu:")
        parser.print_help()

        try:
            user_input = (
                input(
                    f"\n❓ {settings.NROBO_APP} is backed by PyTest. Show PyTest options too? (y/n): "  # noqa: E501
                )  # noqa: E501
                .strip()
                .lower()
            )  # noqa: E501
        except EOFError:
            user_input = "n"  # fallback in non-interactive shells

        if user_input.startswith("y"):
            logger.info("\n📜 Pytest Help Menu:")
            pytest.main(["--help"])
            sys.exit(0)

    # parse_known_args() → splits known vs unknown args safely
    args, unknown_args = parser.parse_known_args()

    # Handle `nrobo --init`
    if args.init:
        initialize_project()
        sys.exit(0)

    try:
        copy_configs_if_updated()
    except FileNotFoundError:
        pass

    # Handle test execution
    suites = args.suite
    browser = args.browser

    if args.debug:
        os.environ["NROBO_DEBUG"] = "True"
        settings.DEBUG = True
        set_logger_level(logger=logger, stream_level=10, file_level=10)
    else:
        os.environ["NROBO_DEBUG"] = "False"
        settings.DEBUG = False

    # update args
    os.environ["NROBO_BROWSER"] = browser

    os.environ["NROBO_HEADLESS"] = str(not args.no_headless)

    if args.coverage:
        unknown_args.extend(
            [
                "--cov=nrobo",  # measure coverage for your framework package
                "--cov-report=html",
                "--cov-report=xml",  # generate HTML report
                "--cov-report=term-missing",  # show missing lines in terminal
                "--cov-fail-under=90",  # fail if coverage < 90%
            ]
        )

    # always change temp dir under project dir
    if not any("--basetemp=" in arg for arg in unknown_args):
        if settings.NROBO_BASENAME_TMP:
            unknown_args.extend(["--basetemp=.pytest_tmp"])

    unknown_args = prepare_reporting_args(pytest_args=unknown_args)
    logger.debug(f"Final PyTest Options=>{unknown_args}")
    return suites, browser, args, unknown_args

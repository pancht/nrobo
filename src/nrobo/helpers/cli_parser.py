import argparse
import sys

import pytest

from nrobo.core import settings
from nrobo.helpers.logging import get_logger
from nrobo.utils.utils import initialize_project

logger = get_logger(name=settings.APP)


def get_nrobo_arg_parser():
    parser = argparse.ArgumentParser(
        description=f"{settings.APP} - Smart Test Runner built on Pytest",
        add_help=True,
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
        help=f"Initialize a new {settings.APP} project with sample suite and tests.",  # noqa: E501
    )

    if "--help" in sys.argv:
        logger.info(f"\n📜 {settings.APP} Help Menu:")
        parser.print_help()

        try:
            user_input = (
                input(
                    f"\n❓ {settings.APP} is backed by PyTest. Show PyTest options too? (y/n): "  # noqa: E501
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

    # Handle test execution
    suites = args.suite
    browser = args.browser
    # e.g., ['-v', '-s', '--maxfail=1']
    return suites, browser, args, unknown_args

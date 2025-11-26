import argparse
import os
import subprocess  # nosec B404
import sys
from pathlib import Path

import pytest

from nrobo.core import settings
from nrobo.helpers.arg_parsing import (
    standardize_allure_reoprt_path,
    standardize_html_reoprt_path,
)
from nrobo.helpers.logging import get_logger

from .helpers._pytest import no_execution_key_found, should_proceed
from .runner import prepare_pytest_cli_options
from .utils.utils import initialize_project


def main():

    logger = get_logger(name=settings.APP)

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
        default="chrome",
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
    pytest_args = unknown_args  # e.g., ['-v', '-s', '--maxfail=1']

    # auto-detect suite(s) if not provided
    if suites is None:
        suites_dir = Path.cwd() / "suites"
        yml_files = list(suites_dir.glob("*.yml"))
        if yml_files:
            # suites = [yml_files[0].name]
            suites = None
            # print(f"No --suite provided. Auto-detected suite: {suites[0]}")
        else:
            logger.info(
                "No suite specified and no suite files found. Running all tests..."  # noqa: E501
            )  # noqa: E501
            suites = [None]

    logger.info(
        f"Starting {settings.APP} test execution on browser: {browser} {"" if args.no_headless else "in headless mode"}..."  # noqa: E501
    )
    logger.info(f"Suites to execute: {suites}")
    logger.info(f"Extra pytest args: {pytest_args}")

    # update args
    os.environ["NROBO_BROWSER"] = browser

    if args.no_headless:
        os.environ["NROBO_HEADLESS"] = "False"
    else:
        os.environ["NROBO_HEADLESS"] = "True"

    # if not any("-n" in arg for arg in pytest_args):
    #     pytest_args.extend(["-n",  "4"])

    if any("--html" in arg for arg in pytest_args):
        pytest_args = standardize_html_reoprt_path(pytest_args)
    else:
        pytest_args.extend(["--html=reports/report.html", "--self-contained-html"])  # noqa: E501

    if any(f"--{settings.REPORT_TYPE_ALLURE}" in arg for arg in pytest_args):
        pytest_args = standardize_allure_reoprt_path(pytest_args)
    else:
        pytest_args.extend([f"--alluredir={settings.ALLURE_RESULTS_DIR}"])

    pytest_options = prepare_pytest_cli_options(
        suites=suites, pytest_args=pytest_args
    )  # noqa: E501
    # print(pytest_options)

    # Uncomment to actually run
    # No need to pass plugin manually to pytest.main
    # As it was already loaded per the lines following in the pyproject.toml
    # This is modern (PEP 621) way of loading plugins
    # -----------------------------------------------------------------------
    #   [project.entry-points.pytest11]
    #   allure_pytest = "allure_pytest.plugin"
    #   xdist = "xdist.plugin"
    #   nrobo = "nrobo.plugin"
    # -----------------------------------------------------------------------
    # instead of the this below:
    #   plugin = nRoboWebDriverPlugin()
    #   pytest.main(args=pytest_options, plugins=[plugin])
    exit_code = pytest.main(args=pytest_options)

    logger.info("\n✅ All suites executed successfully.")

    if not should_proceed(exit_code) or no_execution_key_found(pytest_options):
        # no need to proceed further...
        return 0

    try:
        subprocess.run(  # nosec B603
            [
                "allure",
                "generate",
                settings.ALLURE_RESULTS_DIR,
                "-o",
                settings.ALLURE_REPORT_DIR,
                "--clean",
            ],  # noqa: E501
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(
            f"✅ Allure report ready: file://{os.path.abspath(settings.ALLURE_REPORT_DIR)}/index.html"  # noqa: E501
        )  # noqa: E501
    except subprocess.CalledProcessError as e:
        logger.info("❌ Failed to generate Allure report.")
        logger.info("Command:", e.cmd)
        logger.info("Exit Code:", e.returncode)
        logger.info("Output:", e.output)
        logger.info("Error Output:", e.stderr)


if __name__ == "__main__":
    main()

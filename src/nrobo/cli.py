import os
import subprocess  # nosec B404
from pathlib import Path

import pytest

from nrobo.core import settings
from nrobo.helpers.arg_parsing import (
    standardize_allure_reoprt_path,
    standardize_html_reoprt_path,
)
from nrobo.helpers.cli_parser import get_nrobo_arg_parser
from nrobo.helpers.logging import get_logger
from nrobo.helpers.validations import validate_suite_files

from .helpers._pytest import no_execution_key_found, should_proceed
from .runner import prepare_pytest_cli_options


def main():

    logger = get_logger(name=settings.APP)

    suites, browser, args, pytest_args = get_nrobo_arg_parser()

    # auto-detect suite(s) if not provided
    if suites is None:
        suites_dir = Path.cwd() / settings.SUITES_DIR
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
    else:
        validate_suite_files(suites=suites)

    logger.info(
        f"Starting {settings.APP} test execution on browser: {browser} {"" if args.no_headless else "in headless mode"}..."  # noqa: E501
    )
    logger.info(f"Suites to execute: {suites}")
    logger.info(f"Extra pytest args: {pytest_args}")

    # update args
    os.environ["NROBO_BROWSER"] = browser

    os.environ["NROBO_HEADLESS"] = str(not args.no_headless)

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
            f"✅ Allure report ready: file://{Path(settings.ALLURE_REPORT_DIR).resolve()}/index.html"  # noqa: E501
        )  # noqa: E501
    except subprocess.CalledProcessError as e:
        logger.error("❌ Failed to generate Allure report.")
        logger.error("Command:", e.cmd)
        logger.error("Exit Code:", e.returncode)
        logger.error("Output:", e.output)
        logger.error("Error Output:", e.stderr)


if __name__ == "__main__":
    main()

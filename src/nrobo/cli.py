import argparse
import os
import subprocess
import sys
import pytest
from pathlib import Path

from nrobo.helpers.arg_parsing import standardize_html_reoprt_path, standardize_allure_reoprt_path
from .runner import prepare_pytest_cli_options
from .utils.utils import initialize_project
from .plugin import nRoboWebDriverPlugin


def main():
    parser = argparse.ArgumentParser(
        description="nRoBo - Smart Test Runner built on Pytest",
        add_help=True,
    )

    # known args
    parser.add_argument(
        "--suite",
        nargs="+",  # Accepts multiple values (space-separated)
        help="One or more suite YAML files under suites/ (space-separated or repeated).",
        default=None,
    )
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
        help="Run browser in headed mode (default is headless)"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize a new nRoBo project with sample suite and tests.",
    )

    if "--help" in sys.argv:
        print("\n📜 nRobo Help Menu:")
        parser.print_help()

        try:
            user_input = input("\n❓ nRobo is backed by PyTest. Show PyTest options too? (y/n): ").strip().lower()
        except EOFError:
            user_input = "n"  # fallback in non-interactive shells

        if user_input.startswith("y"):
            print("\n📜 Pytest Help Menu:")
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
            print("No suite specified and no suite files found. Running all tests...")
            suites = [None]

    print(f"Starting nRoBo test execution on browser: {browser} {"" if args.no_headless else "in headless mode"}...")
    print(f"Suites to execute: {suites}")
    print(f"Extra pytest args: {pytest_args}")

    #update args
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
        pytest_args.extend(["--html=reports/report.html", "--self-contained-html"])
    allure_results_dir = "allure-results"
    allure_report_dir = "allure-reports"

    if any("--alluredir" in arg for arg in pytest_args):
        pytest_args = standardize_allure_reoprt_path(pytest_args)
    else:
        pytest_args.extend([f"--alluredir={allure_results_dir}"])

    pytest_options = prepare_pytest_cli_options(suites=suites, pytest_args=pytest_args)
    print(pytest_options)


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
    pytest.main(args=pytest_options)

    print("\n✅ All suites executed successfully.")

    if any("--alluredir" in arg for arg in pytest_options):
        # 2️⃣ Generate allure report (HTML)
        os.makedirs(allure_report_dir, exist_ok=True)
        subprocess.run(["allure", "generate", allure_results_dir, "-o", allure_report_dir, "--clean"], check=True)

        print(f"✅ Allure report ready: file://{os.path.abspath(allure_report_dir)}/index.html")


if __name__ == "__main__":
    main()

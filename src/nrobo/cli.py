import argparse
import sys
import pytest
from pathlib import Path
from .runner import prepare_pytest_cli_options
from .utils import initialize_project


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
        "-b", "--browser",
        help="Browser to run tests on (chrome, firefox, edge, etc.)",
        default="chrome",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize a new nRoBo project with sample suite and tests.",
    )

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
            suites = [yml_files[0].name]
            suites = None
            # print(f"No --suite provided. Auto-detected suite: {suites[0]}")
        else:
            print("No suite specified and no suite files found. Running all tests...")
            suites = [None]

    print(f"Starting nRoBo test execution on browser: {browser} ...")
    print(f"Suites to execute: {suites}")
    print(f"Extra pytest args: {pytest_args}")

    pytest_options = prepare_pytest_cli_options(suite=suites, pytest_args=pytest_args)
    print(f"pytest options => {pytest_options}")
    # Uncomment to actually run
    exit_code = pytest.main(pytest_options)
    if exit_code != 0:
        sys.exit(exit_code)

    print("\n✅ All suites executed successfully.")


if __name__ == "__main__":
    main()

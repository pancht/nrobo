import json
import os
import subprocess
import tempfile
from pathlib import Path
from subprocess import CalledProcessError
from typing import List, Optional, Union

import yaml
from _pytest.config import ExitCode
from _pytest.nodes import Item

from nrobo.core import settings
from nrobo.core.exceptions import (
    NoTestsFoundException,
    ReadSuiteFailed,
    SuiteNotFoundError,
)
from nrobo.helpers.logging_helper import get_logger
from nrobo.utils.common_utils import deduplicate_preserve_order

logger = get_logger(name=settings.NROBO_APP)


def extract_test_name(item: Item) -> str:
    """
    Extracts a clean test method name (optionally with class) from pytest item.nodeid. # noqa: E501
    Handles parametrize, class methods, standalone functions.
    """
    nodeid = item.nodeid  # e.g. tests/test_file.py::TestClass::test_method[param]  # noqa: E501
    parts = nodeid.split("::")

    if len(parts) == 3:
        # Format: file::class::method
        _, cls, method = parts
        return f"{cls}_{method}"
    elif len(parts) == 2:
        # Format: file::method
        _, method = parts
        return method
    else:
        # Fallback to last part
        return parts[-1]


def should_proceed(exit_code) -> bool:
    """Return True if further steps (e.g. report generation) should continue post pytest execution."""  # noqa: E501

    if isinstance(exit_code, int):
        try:
            exit_code = ExitCode(exit_code)
        except ValueError:
            return False  # Unknown code → stop

    return exit_code in (
        ExitCode.OK,
        ExitCode.NO_TESTS_COLLECTED,
        ExitCode.TESTS_FAILED,
    )  # noqa: E501


def no_execution_key_found(args: list):
    return any(arg in ["--co", "--collect-only"] for arg in args)


def detect_fixture_usage(fixture_name: str, test_paths: List[str], pytest_args: List[str]):
    """Check if a specific fixture is used in the given tests using a custom pytest plugin."""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        report_path = Path(tmp.name)

    try:
        os.environ["FIXTURE_REPORT_PATH"] = str(report_path)

        k_option = extract_k_option(pytest_args)

        # Build and deduplicate CLI args
        cmd = deduplicate_preserve_order(
            [
                "pytest",
                "--collect-only",
                "-p",
                "nrobo.plugins.detect_fixtures_plugin",
                "-q",
                *k_option,
                *test_paths,
            ]
        )
        # print(cmd)
        try:
            # Run collection subprocess silently
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except CalledProcessError as cpe:
            # print(cpe)
            if cpe.returncode == 5:
                logger.error("❌ No tests were collected by pytest.")
                logger.warning("ℹ️ Troubleshooting Tips:")
                logger.warning(
                    "  - Check that your test files follow naming conventions (e.g. `test_*.py`)."
                )
                logger.warning(
                    "  - Ensure there are actual test functions/classes inside those files."
                )
                logger.warning("  - Ensure correct `test-file`/`suite-file` is provided.")
                logger.warning(
                    "  - Verify that `pytest_args` and `test_paths` point to valid test files or directories."
                )
                logger.warning(
                    "  - Confirm your environment is properly configured and test paths exist."
                )
            if cpe.returncode == 4:
                logger.error("❌ pytest command line usage error")
                logger.warning("ℹ️ Troubleshooting Tips:")
                logger.warning(
                    "  - Check if arguments passed are correct pytest args. Check following link: https://docs.pytest.org/en/stable/reference/reference.html?utm_source=chatgpt.com#command-line-flags"
                )

            if cpe.returncode in [5, 2]:
                raise NoTestsFoundException()

        with report_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return any(fixture_name in entry.get("fixtures", []) for entry in data)

    finally:
        # Always remove the temp file
        if report_path.exists():
            report_path.unlink()


def extract_k_option(args: list[str]):
    result = []
    skip = False
    for i, arg in enumerate(args):
        if skip:
            skip = False
            continue
        if arg == "-k" and i + 1 < len(args):
            result.extend([arg, args[i + 1]])
            skip = True
    return result


def prepare_pytest_cli_options(
    suites: Optional[Union[str, List[str]]] = None,
    pytest_args: Optional[List[str]] = None,
    test_dir: Optional[Path] = None,
    suite_dir: Optional[Path] = None,
) -> List[str]:
    """
    Build the final list of pytest CLI options based on suite YAML files and extra args.

    Args:
        suites: Single suite file name, list of suite files, or None.
        pytest_args: Additional pytest command-line arguments.
        test_dir: Optional path override for tests dir (used for testing).
        suite_dir: Optional path override for suites dir (used for testing).

    Returns:
        List of pytest CLI arguments to pass to pytest.main().
    """
    test_dir = Path(test_dir or Path.cwd() / settings.TESTS_DIR)
    suite_dir = Path(suite_dir or Path.cwd() / settings.SUITES_DIR)

    selected_tests = [str(test_dir)]

    if suites:
        selected_tests = []
        suite_files = [suites] if isinstance(suites, str) else suites

        for suite_file in suite_files:
            suite_path = suite_dir / suite_file
            if not suite_path.exists():
                raise SuiteNotFoundError(suite_path=suite_path)

            try:
                with suite_path.open(encoding="utf-8") as f:
                    suite_data = yaml.safe_load(f) or {}
            except Exception as e:
                raise ReadSuiteFailed(suite_path=suite_path, reason=e)

            for test_name in suite_data.get("tests", []):
                selected_tests.append(str(test_dir / test_name))

    selected_tests = selected_tests or [str(test_dir)]
    return (pytest_args or []) + selected_tests

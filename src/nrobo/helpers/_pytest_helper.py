import json
import os
import subprocess
import tempfile
from pathlib import Path
from subprocess import CalledProcessError
from typing import List

from _pytest.config import ExitCode
from _pytest.nodes import Item

from nrobo.core import settings
from nrobo.core.exceptions import NoTestsFoundException
from nrobo.helpers.logging_helper import get_logger
from nrobo.utils.common_utils import deduplicate_preserve_order

logger = get_logger(name=settings.APP)


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
    return any("--co" == arg for arg in args)


def detect_fixture_usage(fixture_name: str, test_paths: List[str], pytest_args: List[str]):
    """Check if a specific fixture is used in the given tests using a custom pytest plugin."""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        report_path = Path(tmp.name)

    try:
        os.environ["FIXTURE_REPORT_PATH"] = str(report_path)

        # Build and deduplicate CLI args
        cmd = deduplicate_preserve_order(
            [
                "pytest",
                "--collect-only",
                "-p",
                "nrobo.plugins.detect_fixtures_plugin",
                *pytest_args,
                *test_paths,
            ]
        )

        try:
            # Run collection subprocess silently
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except CalledProcessError as cpe:
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

                raise NoTestsFoundException()

        with report_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return any(fixture_name in entry.get("fixtures", []) for entry in data)

    finally:
        # Always remove the temp file
        if report_path.exists():
            report_path.unlink()

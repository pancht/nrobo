import json
import os
import subprocess
import tempfile

from _pytest.config import ExitCode
from _pytest.nodes import Item

from nrobo.utils.common_utils import deduplicate_preserve_order


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


def detect_fixture_usage(fixture_name, test_paths, pytest_args: list[str]):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        path = tmp.name
    os.environ["FIXTURE_REPORT_PATH"] = path

    cmd = (
        ["pytest", "--collect-only", "-p", "nrobo.plugins.detect_fixtures_plugin"]
        + pytest_args
        + test_paths
    )

    # Redirect subprocess output to subprocess.DEVNULL
    subprocess.run(
        deduplicate_preserve_order(cmd),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    with open(path) as f:
        data = json.load(f)
    return any(fixture_name in entry["fixtures"] for entry in data)

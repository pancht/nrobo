from pathlib import Path
from unittest.mock import patch

import pytest

from nrobo.core import settings
from nrobo.core.exceptions import SuiteNotFoundError
from nrobo.utils.suite_utils import detect_or_validate_suites


@pytest.mark.parametrize(
    "arg_suite, expected",
    [
        (None, []),
        ([""], [""]),
        (["a.yml"], ["a.yml"]),
        (["a.yml", "b.yml"], ["a.yml", "b.yml"]),
        (["a.yml", "a.yml", "b.yml"], ["a.yml", "b.yml"]),
        ("noexistsuite.yml", pytest.raises(SuiteNotFoundError)),
    ],
    ids=[
        "none",
        "empty_string",
        "single_suite",
        "two_suites",
        "duplicates_removed",
        "suite_not_found",
    ],
)
def test_detect_or_validate_returns_suites(arg_suite, expected, tmp_path: Path):
    fake_suites_dir = tmp_path / "suites"
    fake_tests_dir = tmp_path / "tests"

    fake_suites_dir.mkdir(parents=True, exist_ok=True)
    fake_tests_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy .yml suite files
    for name in ["a.yml", "b.yml"]:
        (fake_suites_dir / name).write_text("robot_suite: true\n")

    with (
        patch.object(settings, "SUITES_DIR", fake_suites_dir),
        patch.object(settings, "TESTS_DIR", fake_tests_dir),
    ):

        if hasattr(expected, "__enter__"):  # e.g. if expected is pytest.raises(...)
            with expected:
                detect_or_validate_suites(arg_suite)
        else:
            result = detect_or_validate_suites(arg_suite)
            assert result == expected

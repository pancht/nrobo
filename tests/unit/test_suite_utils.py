from pathlib import Path

import pytest

from nrobo.core import settings
from nrobo.exceptions import SuiteNotFoundError
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
    # create fake suites dir and tests dir
    settings.SUITES_DIR = tmp_path / "suites"
    settings.TESTS_DIR = tmp_path / "tests"

    settings.SUITES_DIR.mkdir(parents=True, exist_ok=True)
    settings.TESTS_DIR.mkdir(parents=True, exist_ok=True)

    # Create fake suite files if needed
    filenames = ["a.yml", "b.yml"]
    created_files = []
    for name in filenames:
        file = settings.SUITES_DIR / name
        file.write_text("robot_suite: true\n")
        created_files.append(str(file))

    if hasattr(expected, "__enter__"):  # pytest.raises is a context manager
        with pytest.raises(SuiteNotFoundError):
            detect_or_validate_suites(arg_suite)
    else:
        result = detect_or_validate_suites(arg_suite)
        assert result == expected


#
#
# @patch("nrobo.utils.suite_utils.resolve_suites", return_value=[])
# def test_detect_or_validate_raises_exception_when_none_found(mock_resolve):
#     with pytest.raises(NoTestsFoundException, match="No test suites"):
#         detect_or_validate_suites([])

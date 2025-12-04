# 🧪 Pytest suite
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from _pytest.config import ExitCode

from nrobo.core import settings
from nrobo.core.exceptions import (
    NoTestsFoundException,
    ReadSuiteFailed,
    SuiteNotFoundError,
)
from nrobo.helpers._pytest_helper import (
    detect_fixture_usage,
    extract_k_option,
    extract_test_name,
    no_execution_key_found,
    prepare_pytest_cli_options,
    should_proceed,
)


# Simulated Pytest Item with nodeid
class DummyItem:
    def __init__(self, nodeid):
        self.nodeid = nodeid


@pytest.mark.parametrize(
    "nodeid, expected",
    [
        # Class method with parameter
        ("tests/test_math.py::TestCalc::test_add[1-2]", "TestCalc_test_add[1-2]"),
        # Standalone function
        ("tests/test_api.py::test_login", "test_login"),
        # Nested class method (e.g. inner class or nested identifier)
        ("tests/test_app.py::Outer::Inner::test_run", "test_run"),
        # No method/class — fallback to last segment
        ("tests/test_standalone.py", "tests/test_standalone.py"),
        # Class method without params
        ("tests/test_core.py::MyClass::test_workflow", "MyClass_test_workflow"),
        # Parameterized standalone test
        ("tests/test_flags.py::test_flags[--dry-run]", "test_flags[--dry-run]"),
    ],
)
def test_extract_test_name(nodeid, expected):
    item = DummyItem(nodeid)
    assert extract_test_name(item) == expected


@pytest.mark.parametrize(
    "code,expected",
    [
        (ExitCode.OK, True),
        (ExitCode.NO_TESTS_COLLECTED, True),
        (ExitCode.TESTS_FAILED, True),
        (ExitCode.INTERRUPTED, False),
        (ExitCode.INTERNAL_ERROR, False),
        (ExitCode.USAGE_ERROR, False),
        (999, False),  # invalid int
        (-1, False),  # invalid int
        ("OK", False),  # invalid type
        (None, False),
    ],
)
def test_should_proceed(code, expected):
    assert should_proceed(code) == expected


@pytest.mark.parametrize(
    "args, expected",
    [
        (["--co"], True),  # Exact match
        (["--co", "--other"], True),  # With other args
        (["--collect-only"], True),  # Similar but not exact
        (["--co="], False),  # Prefix only
        (["--c"], False),  # Partial
        (["--CO"], False),  # Case sensitive
        ([], False),  # Empty list
    ],
)
def test_no_execution_key_found(args, expected):
    assert no_execution_key_found(args) == expected


@pytest.mark.parametrize(
    "args, expected",
    [
        (
            [
                "--html=out.html",
                "--self-contained-html",
                "-k",
                "test_keyword",
                "--alluredir",
                "results",
            ],
            ["-k", "test_keyword"],
        ),
        (["--html=out.html", "--self-contained-html", "--alluredir", "results"], []),
        (["-k", "some_test", "-k", "another_test"], ["-k", "some_test", "-k", "another_test"]),
        (["-k"], []),  # Edge case: -k without a value
        ([], []),  # Empty input
    ],
    ids=[
        "single -k option",
        "no -k option",
        "multiple -k options",
        "-k with no value",
        "empty args list",
    ],
)
def test_extract_k_option(args, expected):
    assert extract_k_option(args) == expected


@pytest.mark.parametrize("code", [5, 4, 2])
def test_detect_fixture_usage_cpe_handling(tmp_path, code):
    fake_report = tmp_path / "fixture_report.json"
    fake_report.write_text("[]")

    with (
        patch("nrobo.helpers._pytest_helper.tempfile.NamedTemporaryFile") as mock_tmp,
        patch("nrobo.helpers._pytest_helper.subprocess.run") as mock_run,
        patch("nrobo.helpers._pytest_helper.Path.exists", return_value=True),
        patch("nrobo.helpers._pytest_helper.Path.unlink"),
        patch("nrobo.helpers._pytest_helper.Path.open", create=True) as mock_open,
    ):

        # Simulate the temp file path
        mock_tmp.return_value.__enter__.return_value.name = str(fake_report)
        mock_open.return_value.__enter__.return_value.read.return_value = "[]"
        mock_open.return_value.__enter__.return_value.__iter__.return_value = iter(["[]"])
        mock_open.return_value.__enter__.return_value.read.return_value = "[]"

        # Simulate CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(returncode=code, cmd="pytest")

        if code in [5, 2]:
            with pytest.raises(NoTestsFoundException):
                detect_fixture_usage("nrobo", ["tests/"], ["-k", "some_test"])
        else:
            # should not raise for code 4 alone
            result = detect_fixture_usage("nrobo", ["tests/"], ["-k", "some_test"])
            assert result is False


def write_suite_file(path: Path, data: dict):
    """Helper to write a YAML suite file at `path`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


def test_no_suites_defaults_to_tests_dir(tmp_path):
    """
    If no suites are provided, the function should return pytest_args (if any)
    plus the default tests directory.
    """
    with (
        patch.object(settings, "TESTS_DIR", "my_tests"),
        patch.object(settings, "SUITES_DIR", "my_suites"),
        patch("pathlib.Path.cwd", return_value=tmp_path),
    ):

        pytest_args = ["--verbose", "-q"]
        result = prepare_pytest_cli_options(
            suites=None,
            pytest_args=pytest_args,
            test_dir=None,
            suite_dir=None,
        )

        expected_default_tests = str(tmp_path / "my_tests")
        assert result == pytest_args + [expected_default_tests]


def test_single_suite_file_with_tests(tmp_path, monkeypatch):
    """
    If a valid suite YAML file is provided, return its listed tests (prefixed by tests/)
    """
    monkeypatch.setattr(settings, "TESTS_DIR", "tests_dir")
    monkeypatch.setattr(settings, "SUITES_DIR", "suites_dir")
    monkeypatch.chdir(tmp_path)

    # Prepare directories and suite file
    suite_name = "suite1.yml"
    suite_dir = tmp_path / "suites_dir"
    suite_file = suite_dir / suite_name
    # Create a fake test file entry
    suite_data = {"tests": ["test_a.py", "subdir/test_b.py"]}
    write_suite_file(suite_file, suite_data)

    # Run
    result = prepare_pytest_cli_options(
        suites=suite_name,
        pytest_args=None,
        test_dir=None,
        suite_dir=None,
    )

    # Assert that result equals the test paths derived from suite_data
    expected = [
        str(tmp_path / "tests_dir" / "test_a.py"),
        str(tmp_path / "tests_dir" / "subdir" / "test_b.py"),
    ]
    assert result == expected


def test_multiple_suites_list(tmp_path, monkeypatch):
    """
    If a list of suite names is provided, it should accumulate tests from all.
    """
    monkeypatch.setattr(settings, "TESTS_DIR", "t")
    monkeypatch.setattr(settings, "SUITES_DIR", "s")
    monkeypatch.chdir(tmp_path)

    # suite1
    s1 = "s1.yml"
    write_suite_file(tmp_path / "s" / s1, {"tests": ["a.py"]})
    # suite2
    s2 = "s2.yml"
    write_suite_file(tmp_path / "s" / s2, {"tests": ["b.py", "c.py"]})

    result = prepare_pytest_cli_options(
        suites=[s1, s2],
        pytest_args=["--flag"],
        test_dir=None,
        suite_dir=None,
    )

    expected = [
        "--flag",
        str(tmp_path / "t" / "a.py"),
        str(tmp_path / "t" / "b.py"),
        str(tmp_path / "t" / "c.py"),
    ]
    assert result == expected


def test_suite_not_found_raises(tmp_path, monkeypatch):
    """
    If the suite file does not exist, should raise SuiteNotFoundError.
    """
    monkeypatch.setattr(settings, "SUITES_DIR", "suites")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SuiteNotFoundError) as excinfo:
        prepare_pytest_cli_options(suites="nonexistent.yml")

    assert "nonexistent.yml" in str(excinfo.value)


def test_invalid_yaml_raises_ReadSuiteFailed(tmp_path, monkeypatch):
    """
    If the suite file has invalid YAML / cannot be parsed, should raise ReadSuiteFailed.
    """
    monkeypatch.setattr(settings, "SUITES_DIR", "suites")
    monkeypatch.setattr(settings, "TESTS_DIR", "tests")
    monkeypatch.chdir(tmp_path)

    bad = tmp_path / "suites" / "bad.yml"
    bad.parent.mkdir(parents=True, exist_ok=True)
    # Write invalid YAML
    bad.write_text("::: not valid yaml :::", encoding="utf-8")

    with pytest.raises(ReadSuiteFailed) as excinfo:
        prepare_pytest_cli_options(suites="bad.yml")

    assert "bad.yml" in str(excinfo.value)


def test_empty_tests_list_or_no_tests_field(tmp_path, monkeypatch):
    """
    If suite YAML is empty or 'tests' missing, should default to tests directory.
    """
    monkeypatch.setattr(settings, "TESTS_DIR", "testsdir")
    monkeypatch.setattr(settings, "SUITES_DIR", "suitesdir")
    monkeypatch.chdir(tmp_path)

    suite_name = "empty.yml"
    write_suite_file(tmp_path / "suitesdir" / suite_name, {})  # empty YAML

    result = prepare_pytest_cli_options(suites=suite_name)

    # Should point to default tests dir
    expected = [str(tmp_path / "testsdir")]
    assert result == expected

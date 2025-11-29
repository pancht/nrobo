# 🧪 Pytest suite

import pytest
from _pytest.config import ExitCode

from nrobo.helpers._pytest_helper import (
    extract_test_name,
    no_execution_key_found,
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

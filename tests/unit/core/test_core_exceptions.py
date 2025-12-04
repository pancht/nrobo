# 🔍 Test for ReadSuiteFailed
from pathlib import Path

import pytest

from nrobo.core.constants import ExitCodes
from nrobo.core.exceptions import (
    DependencyNotFoundError,
    NoTestsFoundException,
    NRoboError,
    ReadSuiteFailed,
)


@pytest.mark.parametrize("reason", [None, "invalid yaml", ValueError("Missing colon")])
def test_read_suite_failed_exception(reason):
    path = Path("/fake/path/suite.yaml")

    # Act
    exc = ReadSuiteFailed(path, reason)

    # Assert attributes
    assert isinstance(exc, NRoboError)
    assert exc.suite_path == path
    assert exc.reason == reason
    assert exc.return_code == ExitCodes.READ_SUITE_FAILED

    # Assert message formatting
    base_msg = f"⚠️ Failed to read suite: {path}"
    if reason:
        assert str(exc).startswith(base_msg)
        assert "→ Reason:" in str(exc)
        assert str(reason) in str(exc)
    else:
        assert str(exc) == base_msg


@pytest.mark.parametrize(
    "reason, search_path, expected_reason, expected_path",
    [
        (None, None, "No test suites or pytest test files were detected.", None),
        ("Custom reason here", None, "Custom reason here", None),
        (
            "Another custom reason",
            "/some/test/path",
            "Another custom reason",
            Path("/some/test/path"),
        ),
    ],
)
def test_no_tests_found_exception(reason, search_path, expected_reason, expected_path):
    # Act
    exc = NoTestsFoundException(reason=reason, search_path=search_path)

    # Assert: correct inheritance
    assert isinstance(exc, NRoboError)

    # Assert: attributes
    assert exc.reason == expected_reason
    assert exc.search_path == expected_path
    assert exc.return_code == ExitCodes.NO_TESTS_FOUND

    # Assert: message
    base_msg = f"❌ {expected_reason}"
    msg = str(exc)

    assert msg.startswith(base_msg)
    if expected_path:
        assert f"🔍 Searched in: {expected_path}" in msg
    else:
        assert "🔍 Searched in:" not in msg


def test_dependency_not_found_error_with_hint():
    hint = "Run `brew install git`"
    try:
        raise DependencyNotFoundError("git", install_hint=hint)
    except DependencyNotFoundError as e:
        assert "git" in str(e)
        assert hint in str(e)
        assert e.return_code == ExitCodes.DEP_NOT_FOUND

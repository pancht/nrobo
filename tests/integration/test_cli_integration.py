import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from nrobo import cli
from nrobo.core import settings
from nrobo.helpers.test_data_helper import _create_passing_test


def test_cli_run_executes_tests_and_returns_correct_exit_code(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """✅ Runs cli.run() with real test file and checks CLI output and exit code."""

    fake_tests = tmp_path / "tests"
    fake_suites = tmp_path / "suites"
    fake_suites.mkdir(parents=True)

    _create_passing_test(fake_tests)

    with (
        patch.object(settings, "TESTS_DIR", fake_tests),
        patch.object(settings, "SUITES_DIR", fake_suites),
        patch.object(sys, "argv", ["nrobo", str(fake_tests)]),
        caplog.at_level("INFO"),
    ):
        exit_code = cli.run()

    assert exit_code == 0
    assert "test execution on browser:" in caplog.text or "non-browser tests" in caplog.text
    assert "✅ All suites/tests executed successfully." in caplog.text
    assert "✅ Allure report ready  →" in caplog.text

# test/test_cli_integration.py
import sys
import textwrap
from pathlib import Path
from unittest import mock
from unittest.mock import patch

import pytest

from nrobo import cli
from nrobo.core import settings


def test_cli_run_executes_tests_and_returns_correct_exit_code(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """Mocks settings paths and runs cli.run() with real tests."""

    fake_tests_dir = tmp_path / "tests"
    fake_suites_dir = tmp_path / "suites"

    fake_tests_dir.mkdir(parents=True)
    fake_suites_dir.mkdir(parents=True)

    test_code = textwrap.dedent(
        """
        def test_addition():
            assert 1 + 1 == 2
    """
    )

    # Create a real passing test file
    (fake_tests_dir / "test_sample.py").write_text(test_code)

    with (
        patch.object(settings, "TESTS_DIR", fake_tests_dir),
        patch.object(settings, "SUITES_DIR", fake_suites_dir),
        mock.patch.object(sys, "argv", ["nrobo", str(fake_tests_dir)]),
    ):

        with caplog.at_level("INFO"):
            exit_code = cli.run()

    assert exit_code == 0

    # ✅ Output should contain key CLI messages
    assert (
        "🚀 Starting nRobo test execution on browser:" in caplog.text
        or "Running non-browser tests..." in caplog.text
    )
    assert "✅ All suites/tests executed successfully." in caplog.text
    assert "✅ Allure report ready  →" in caplog.text

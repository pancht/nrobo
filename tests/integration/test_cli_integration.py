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

    with (
        patch.object(settings, "TESTS_DIR", fake_tests),
        patch.object(settings, "SUITES_DIR", fake_suites),
        patch.object(sys, "argv", ["nrobo", "--init", "-s"]),
        caplog.at_level("INFO"),
    ):
        try:
            exit_code = cli.run()
        except SystemExit:
            pass

    assert f"{settings.APP} project initialized!" in caplog.text
    assert "📂 Created: suites/, tests/" in caplog.text
    assert "🧩 Added: sample_suite.yml + test_sample.py + test_sample_another.py" in caplog.text

    project_struct = [
        fake_suites / "sample_suite.yml",
        fake_tests / "api",
        fake_tests / "mobile",
        fake_tests / "ui",
        fake_tests / "ui" / "test_sample.py",
    ]

    for each_project_item in project_struct:
        assert each_project_item.exists()

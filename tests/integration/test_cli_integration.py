import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nrobo import cli
from nrobo.core import settings
from nrobo.helpers.test_helper import _create_a_failing_ui_test, _create_a_passing_test


@patch(
    "allure_commons.reporter.ThreadContextItems.__getitem__",
    side_effect=lambda self, item: self.thread_context.get(item, {}),
)
def test_cli_run_executes_tests_and_returns_correct_exit_code(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """✅ Runs cli.run() with real test file and checks CLI output and exit code."""

    fake_tests = tmp_path / "tests"
    fake_suites = tmp_path / "suites"
    fake_suites.mkdir(parents=True)
    fake_allure_results_dir = tmp_path / "allure-results"
    fake_allure_results_dir.mkdir(parents=True, exist_ok=True)
    fake_allure_reports_dir = tmp_path / "allure-reports"
    fake_allure_reports_dir.mkdir(parents=True, exist_ok=True)

    with (
        patch.object(settings, "TESTS_DIR", fake_tests),
        patch.object(settings, "SUITES_DIR", fake_suites),
        patch.object(settings, "ALLURE_RESULTS_DIR", fake_allure_results_dir),
        patch.object(settings, "ALLURE_REPORT_DIR", fake_allure_reports_dir),
        patch.object(sys, "argv", ["nrobo", "--init"]),
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

    _create_a_passing_test(fake_tests)
    _create_a_failing_ui_test(fake_tests)

    with (
        patch.object(settings, "TESTS_DIR", fake_tests),
        patch.object(settings, "SUITES_DIR", fake_suites),
        patch.object(settings, "ALLURE_RESULTS_DIR", fake_allure_results_dir),
        patch.object(settings, "ALLURE_REPORT_DIR", fake_allure_reports_dir),
        patch.object(
            sys,
            "argv",
            [
                "nrobo",
                str(fake_tests),
                f"--alluredir={str(fake_allure_reports_dir / "report.html")}",
            ],
        ),
        patch("nrobo.cli.Path") as mock_path_cls,
        caplog.at_level("INFO"),
    ):
        mock_allure_path = MagicMock(spec=Path)
        mock_allure_path.exists.return_value = True
        mock_allure_path.iterdir.return_value = iter([])

        mock_path_cls.return_value = mock_allure_path

        exit_code = cli.run()

    assert exit_code == 0
    assert "test execution on browser:" in caplog.text or "non-browser tests" in caplog.text
    assert "⚠️ Skipping Allure report — no results found" in caplog.text

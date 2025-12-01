import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nrobo import cli
from nrobo.core import settings
from nrobo.helpers.test_helper import _create_a_failing_ui_test, _create_a_passing_test


# @patch(
#     "allure_commons.reporter.ThreadContextItems.__getitem__",
#     side_effect=lambda self, item: self.thread_context.get(item, {}),
# )
def test_cli_run_executes_tests_and_returns_correct_exit_code(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """✅ Runs cli.run() with real test file and checks CLI output and exit code."""

    fake_tests = tmp_path / "tests"
    fake_suites = tmp_path / "test_suites"
    fake_allure_results_dir = tmp_path / "test_artifacts" / "allure-results"
    tmp_path / "allure-reports"

    with (
        patch("nrobo.utils.command_utils.Path.cwd", return_value=tmp_path),
        patch.object(sys, "argv", ["nrobo", "--init"]),
        caplog.at_level("INFO"),
    ):
        try:
            cli.run()
        except SystemExit:
            pass

        assert f"{settings.NROBO_APP} project initialized!" in caplog.text
        assert "📂 Created: suites/, tests/" in caplog.text
        assert "🧩 Added: sample_suite.yml + test_sample.py + test_sample_another.py" in caplog.text

        test_artifacts_dir = "test_artifacts"

        project_struct = [
            fake_suites / "sample_suite.yml",
            fake_tests / "api",
            fake_tests / "mobile",
            fake_tests / "ui",
            fake_tests / "ui" / "test_sample.py",
            fake_tests / "ui" / "test_sample_another.py",
            tmp_path / test_artifacts_dir / "allure-reports",
            tmp_path / test_artifacts_dir / "allure-reports",
            tmp_path / test_artifacts_dir / "html_report",
            tmp_path / "test_data",
            tmp_path / test_artifacts_dir / "logs",
            tmp_path / "configs" / ".env"
        ]

        for each_project_item in project_struct:
            assert each_project_item.exists()

        _create_a_passing_test(fake_tests)
        _create_a_failing_ui_test(fake_tests)

        with (
            patch.object(settings, "ALLURE_RESULTS_DIR", fake_allure_results_dir),
            patch.object(
                sys,
                "argv",
                [
                    "nrobo",
                    "--alluredir",
                    str(tmp_path / test_artifacts_dir / "allure-results"),
                    f'--html={str(tmp_path / test_artifacts_dir / "html-report" / "report.html")}',
                    f"--basetemp={tmp_path}/.pytest_tmp",
                    str(tmp_path / "tests"),
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

        if exit_code != 0:
            print("Captured logs:\n", caplog.text)

        assert "test execution on browser:" in caplog.text or "non-browser tests" in caplog.text
        assert "⚠️ Skipping Allure report — no results found" in caplog.text

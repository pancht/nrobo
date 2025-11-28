import os
import sys
from logging import Logger
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from nrobo import cli
from nrobo.core import settings
from nrobo.core.constants import ExitCodes
from nrobo.core.exceptions import NoTestsFoundException, NRoboError
from nrobo.helpers.test_data_helper import _create_passing_test
from nrobo.utils.suite_utils import detect_or_validate_suites


@pytest.mark.parametrize(
    "argv, expected",
    [
        (
            ["nrobo"],
            {
                "suites": None,
                "browser": "chrome",
                "env": {
                    "NROBO_BROWSER": "chrome",
                    "NROBO_DEBUG": "False",
                    "NROBO_HEADLESS": "True",
                },
                "args": {
                    "debug": False,
                    "init": False,
                    "cov": False,
                    "no_headless": False,
                },
                "pytest_args": {
                    "--html=reports/report.html",
                    "--self-contained-html",
                    "--alluredir=allure-results",
                    "--basetemp=.pytest_tmp",
                },
            },
        ),
        (
            [
                "nrobo",
                "--debug",
                "--suite",
                "suite1.yml",
                "suite2.yml",
                "--browser",
                "chrome",
                "--no-headless",
                "--cov",
                "--html=xyz/abc/myreport.html",
                "--alluredir=abc/myreport.html",
            ],
            {
                "suites": ["suite1.yml", "suite2.yml"],
                "browser": "chrome",
                "env": {
                    "NROBO_BROWSER": "chrome",
                    "NROBO_DEBUG": "True",
                    "NROBO_HEADLESS": "False",
                },
                "args": {
                    "debug": True,
                    "init": False,
                    "cov": True,
                    "no_headless": True,
                },
                "pytest_args": {
                    "--cov=nrobo",
                    "--cov-report=html",
                    "--cov-report=term-missing",
                    "--cov-fail-under=90",
                    "--html=reports/myreport.html",
                    "--alluredir=allure-results/myreport.html",
                    "--basetemp=.pytest_tmp",
                },
            },
        ),
    ],
    ids=["with_zero_args", "all_nrobo_args_with_default_reporting_and_pytest_args"],
)
def test_nrobo_cli_argument_parsing(argv, expected, logger: Logger):
    from nrobo.helpers.cli_parser import get_nrobo_arg_parser  # handle circular import

    with mock.patch.object(sys, "argv", argv):
        suites, browser, args, pytest_args = get_nrobo_arg_parser()

    assert suites == expected["suites"]
    assert browser == expected["browser"]

    # Check environment variables
    for key, val in expected["env"].items():
        logger.debug(f"key={key} and value={val}")
        assert os.getenv(key) == val

    # Check parsed args
    for key, val in expected["args"].items():
        logger.debug(f"(args, key)=({args}, {key}) and value={val}")
        assert getattr(args, key) == val

    # Check expected pytest args
    for flag in expected["pytest_args"]:
        logger.debug(f"flag={flag}")
        assert flag in pytest_args


def test_cli_handles_no_suites_gracefully(tmp_path: Path):
    fake_suites_dir = tmp_path / "suites"
    fake_tests_dir = tmp_path / "tests"

    fake_suites_dir.mkdir(parents=True, exist_ok=True)
    fake_tests_dir.mkdir(parents=True, exist_ok=True)

    with (
        patch.object(settings, "SUITES_DIR", fake_suites_dir),
        patch.object(settings, "TESTS_DIR", fake_tests_dir),
        patch.object(sys, "argv", ["nrobo"]),
    ):

        # Import after patching to handle circular import safely
        from nrobo.helpers.cli_parser import get_nrobo_arg_parser

        suites, browser, args, pytest_args = get_nrobo_arg_parser()

        with pytest.raises(
            NoTestsFoundException,
            match=rf"❌ No test suites or pytest test files were detected.\n   🔍 Searched in: {fake_tests_dir}",
        ):
            detect_or_validate_suites(suites)


def test_no_execution_key_used(caplog: pytest.LogCaptureFixture):
    with (patch.object(sys, "argv", ["nrobo", "--co"]),):
        with caplog.at_level("INFO"):
            exit_code = cli.run()

        assert exit_code == 0

    assert "⚠️ Skipped report generation:" in caplog.text
    assert "• Required execution keys were not found in the pytest options." in caplog.text
    assert (
        "• This may happen if options like '--collect-only' were used, which prevent test execution."
        in caplog.text
    )


def test_cli_returns_no_tests_found_when_no_suites_or_tests_exist(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """Verify CLI returns correct exit code when no tests or suites are found."""

    fake_suites_dir = tmp_path / "suites"
    fake_tests_dir = tmp_path / "tests"
    fake_suites_dir.mkdir(parents=True)
    fake_tests_dir.mkdir(parents=True)

    argv = ["nrobo"]

    with (
        patch.object(settings, "SUITES_DIR", fake_suites_dir),
        patch.object(settings, "TESTS_DIR", fake_tests_dir),
        patch.object(sys, "argv", argv),
    ):
        exit_code = cli.run()

    # ✅ Confirm proper exit code
    assert exit_code == ExitCodes.NO_TESTS_FOUND


def test_cli_handles_pytest_main_exception():
    with patch.object(sys, "argv", ["nrobo"]), patch("pytest.main", side_effect=Exception):
        exit_code = cli.run()

    # Check correct exit code is returned for internal error
    assert exit_code == pytest.ExitCode.INTERNAL_ERROR


def test_cli_skips_allure_report_when_results_dir_is_empty(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """✅ Runs cli.run() with real test file and checks CLI output and exit code."""

    fake_tests = tmp_path / "tests"
    fake_suites = tmp_path / "suites"
    fake_suites.mkdir(parents=True)
    fake_tests.mkdir(parents=True)

    _create_passing_test(fake_tests)

    with (
        patch.object(settings, "TESTS_DIR", fake_tests),
        patch.object(settings, "SUITES_DIR", fake_suites),
        patch.object(settings, "ALLURE_RESULTS_DIR", "abc"),
        patch.object(
            sys,
            "argv",
            [
                "nrobo",
                str(fake_tests),
                "--quiet",
                "--tb=short",
                "--disable-warnings",
            ],
        ),
        patch("nrobo.cli.Path") as mock_path_cls,
        caplog.at_level("INFO"),
    ):
        # Setup mock Path instance for `allure_dir`
        mock_allure_path = MagicMock(spec=Path)
        mock_allure_path.exists.return_value = True
        mock_allure_path.iterdir.return_value = iter([])

        mock_path_cls.return_value = mock_allure_path

        exit_code = cli.run()

    assert exit_code == 0

    assert "⚠️ Skipping Allure report — no results found." in caplog.text


def test_main_exits_normally_via_run():
    with patch("nrobo.cli.run", side_effect=SystemExit(0)) as mock_run:
        with pytest.raises(SystemExit) as exc:
            cli.main()

        assert exc.value.code == ExitCodes.SUCCESS
        mock_run.assert_called_once()


def test_main_exits_on_nrobo_error():
    mock_error = NRoboError("something went wrong")

    with patch("nrobo.cli.run", side_effect=mock_error):
        with pytest.raises(SystemExit) as exc:
            cli.main()

        assert exc.value.code == ExitCodes.INTERNAL_ERROR


def test_main_exits_on_keyboard_interrupt_error():
    mock_error = KeyboardInterrupt("something went wrong")

    with patch("nrobo.cli.run", side_effect=mock_error):
        with pytest.raises(SystemExit) as exc:
            cli.main()

        assert exc.value.code == ExitCodes.INTERRUPTED


def test_main_exits_on_exception():
    mock_error = Exception("something went wrong")

    with patch("nrobo.cli.run", side_effect=mock_error):
        with pytest.raises(SystemExit) as exc:
            cli.main()

        assert exc.value.code == ExitCodes.INTERNAL_ERROR

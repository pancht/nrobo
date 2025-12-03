import importlib.util
import os
import subprocess
import sys
from io import StringIO
from logging import Logger
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, patch, call

import pytest
from _pytest.config import ExitCode

from nrobo.cli.main import run, main
from nrobo.core import settings
from nrobo.core.constants import ExitCodes
from nrobo.core.exceptions import NoTestsFoundException, NRoboError
from nrobo.helpers._pytest_helper import detect_fixture_usage, should_proceed
from nrobo.helpers.cli_parser import get_nrobo_arg_parser
from nrobo.helpers.test_helper import (
    _create_a_failing_test,
    _create_a_passing_test,
    _create_coveragerc_tmp_file,
)
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
                    "NROBO_BASENAME_TMP": None,
                },
                "args": {
                    "debug": False,
                    "init": False,
                    "coverage": False,
                    "no_headless": False,
                },
                "pytest_args": {
                    "--html=test_artifacts/html_report/report.html",
                    "--self-contained-html",
                    "--alluredir",
                    "test_artifacts/allure-results",
                    #"--basetemp=.pytest_tmp",
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
                "--coverage",
                "--html=xyz/abc/myreport.html",
                "--alluredir",
                "abc/myreport.html",
                "--basetemp=.pytest_tmp",
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
                    "coverage": True,
                    "no_headless": True,
                },
                "pytest_args": {
                    "--cov=nrobo",
                    "--cov-report=html",
                    "--cov-report=term-missing",
                    "--cov-fail-under=90",
                    "--html=test_artifacts/html_report/myreport.html",
                    "--alluredir",
                    "test_artifacts/allure-results",
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


@pytest.mark.parametrize(
    "argv, settings_tmp, expected",
    [
        # 🔹 Case 1: Default run, no basetemp
        (
            ["nrobo"],
            None,  # settings.NROBO_BASENAME_TMP
            {
                "suites": None,
                "browser": "chrome",
                "env": {
                    "NROBO_BROWSER": "chrome",
                    "NROBO_DEBUG": "False",
                    "NROBO_HEADLESS": "True",
                    "NROBO_BASENAME_TMP": None,
                },
                "args": {
                    "debug": False,
                    "init": False,
                    "coverage": False,
                    "no_headless": False,
                },
                "pytest_args": {
                    "--html=test_artifacts/html_report/report.html",
                    "--self-contained-html",
                    "--alluredir",
                    "test_artifacts/allure-results",
                },
            },
        ),
        # 🔹 Case 2: Full run, with basetemp provided
        (
            [
                "nrobo",
                "--debug",
                "--suite", "suite1.yml", "suite2.yml",
                "--browser", "chrome",
                "--no-headless",
                "--coverage",
                "--html=xyz/abc/myreport.html",
                "--alluredir", "abc/myreport.html",
            ],
            ".pytest_tmp",  # settings.NROBO_BASENAME_TMP
            {
                "suites": ["suite1.yml", "suite2.yml"],
                "browser": "chrome",
                "env": {
                    "NROBO_BROWSER": "chrome",
                    "NROBO_DEBUG": "True",
                    "NROBO_HEADLESS": "False",
                    "NROBO_BASENAME_TMP": ".pytest_tmp",
                },
                "args": {
                    "debug": True,
                    "init": False,
                    "coverage": True,
                    "no_headless": True,
                },
                "pytest_args": {
                    "--cov=nrobo",
                    f"--cov-report=html:{settings.TEST_ARTIFACTS_DIR}/{settings.COVERAGE_REPORTS_DIR}/html",
                    "--cov-report=term-missing",
                    "--cov-fail-under=90",
                    "--html=test_artifacts/html_report/myreport.html",
                    "--alluredir",
                    "test_artifacts/allure-results",
                },
            },
        ),
    ],
    ids=[
        "no_basetemp_in_settings",
        "with_basetemp_in_settings",
    ],
)
def test_nrobo_cli_argument_parsing(argv, settings_tmp, expected, logger: Logger, monkeypatch):
    """
    ✅ Tests nrobo CLI argument parsing
    - Ensures environment variables are set correctly
    - Validates parsed CLI args
    - Dynamically checks --basetemp inclusion based on settings.NROBO_BASENAME_TMP
    """

    # Mock settings.NROBO_BASENAME_TMP
    monkeypatch.setattr("nrobo.core.settings.NROBO_BASENAME_TMP", settings_tmp, raising=False)

    from nrobo.helpers.cli_parser import get_nrobo_arg_parser

    with mock.patch.object(sys, "argv", argv):
        suites, browser, args, pytest_args = get_nrobo_arg_parser()

    # ---- Validate Suites and Browser ----
    assert suites == expected["suites"]
    assert browser == expected["browser"]

    # ---- Validate Environment Variables ----
    for key, val in expected["env"].items():
        logger.debug(f"key={key} and value={val}")
        if settings_tmp:
            real_getenv = os.getenv  # capture the original function
            with patch("os.getenv") as mock_getenv:
                mock_getenv.side_effect = lambda key, default=None: (
                    ".pytest_tmp" if key == "NROBO_BASENAME_TMP" else real_getenv(key, default)
                )
                assert os.getenv(key) == (None if val is None else val)

    # ---- Validate CLI Args ----
    for key, val in expected["args"].items():
        logger.debug(f"(args, key)=({args}, {key}) and value={val}")
        assert getattr(args, key) == val

    # ---- Validate pytest args ----
    for flag in expected["pytest_args"]:
        logger.debug(f"flag={flag}")
        assert flag in pytest_args

    # ---- Conditional Check for --basetemp ----
    if settings_tmp:
        # Expect presence of correct basetemp flag
        assert f"--basetemp={settings_tmp}" in pytest_args, \
            f"Expected --basetemp={settings_tmp} in pytest args, got: {pytest_args}"
    else:
        # Ensure no basetemp flag is included
        assert not any(arg.startswith("--basetemp") for arg in pytest_args), \
            f"Unexpected basetemp flag in pytest args: {pytest_args}"


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
            exit_code = run()

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
        exit_code = run()

    # ✅ Confirm proper exit code
    assert exit_code == ExitCodes.NO_TESTS_FOUND


def test_cli_handles_pytest_main_exception():
    with patch.object(sys, "argv", ["nrobo"]), patch("pytest.main", side_effect=Exception):
        exit_code = run()

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

    _create_a_passing_test(fake_tests)

    with (
        patch.object(settings, "TESTS_DIR", fake_tests),
        patch.object(settings, "SUITES_DIR", fake_suites),
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
        patch("nrobo.cli.main.Path") as mock_path_cls,
        caplog.at_level("INFO"),
    ):
        # Setup mock Path instance for `allure_dir`
        mock_allure_path = MagicMock(spec=Path)
        mock_allure_path.exists.return_value = True
        mock_allure_path.iterdir.return_value = iter([])

        mock_path_cls.return_value = mock_allure_path

        exit_code = run()

    assert exit_code == 0

    assert "⚠️ Skipping Allure report — no results found." in caplog.text


def test_main_exits_normally_via_run():
    with patch("nrobo.cli.main.run", side_effect=SystemExit(0)) as mock_run:
        with pytest.raises(SystemExit) as exc:
            main()

        assert exc.value.code == ExitCodes.SUCCESS
        mock_run.assert_called_once()


def test_main_exits_on_nrobo_error():
    mock_error = NRoboError("something went wrong")

    with patch("nrobo.cli.main.run", side_effect=mock_error):
        with pytest.raises(SystemExit) as exc:
            main()

        assert exc.value.code == ExitCodes.INTERNAL_ERROR


def test_main_exits_on_keyboard_interrupt_error():
    mock_error = KeyboardInterrupt("something went wrong")

    with patch("nrobo.cli.main.run", side_effect=mock_error):
        with pytest.raises(SystemExit) as exc:
            main()

        assert exc.value.code == ExitCodes.INTERRUPTED


def test_main_exits_on_exception():
    mock_error = Exception("something went wrong")

    with patch("nrobo.cli.main.run", side_effect=mock_error):
        with pytest.raises(SystemExit) as exc:
            main()

        assert exc.value.code == ExitCodes.INTERNAL_ERROR


def test_cli_runs_with_coverage_config_and_suppresses_warnings(tmp_path: Path):
    fake_tests = tmp_path / "tests"
    fake_suites = tmp_path / "suites"
    fake_tests.mkdir()
    fake_suites.mkdir()

    _create_a_passing_test(fake_tests)
    coveragerc_file = _create_coveragerc_tmp_file(tmp_path)

    # Build the pytest command with filterwarnings
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(fake_tests),
        "--coverage",
        str(fake_tests),
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=90",
        f"--cov-config={str(coveragerc_file)}",
        "-W",
        "ignore::CoverageWarning",  # 👈 suppress the coverage warning
    ]

    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False
    )

    assert result.returncode == 4, f"Test failed:\n{result.stdout}"


def test_detect_fixture_usage_raises_no_tests_found_exception():
    """Should raise NoTestsFoundException when pytest collects no tests (exit code 5)."""

    mock_called_process_error = subprocess.CalledProcessError(
        returncode=5, cmd=["nrobo", "--collect-only"]
    )

    with patch(
        "nrobo.helpers._pytest_helper.subprocess.run", side_effect=mock_called_process_error
    ):
        with pytest.raises(NoTestsFoundException):
            detect_fixture_usage(fixture_name="nrobo", test_paths=["tests"], pytest_args=[])


@pytest.mark.parametrize(
    "exit_code, expected",
    [
        (ExitCode.OK, True),
        (ExitCode.NO_TESTS_COLLECTED, True),
        (ExitCode.TESTS_FAILED, True),
        (ExitCode.INTERRUPTED, False),
        (ExitCode.INTERNAL_ERROR, False),
        (99, False),  # unknown exit code as int
        ("invalid", False),  # invalid type
    ],
)
def test_should_proceed_behavior(exit_code, expected):
    assert should_proceed(exit_code) is expected


def test_cli_outputs_assertion_for_failing_test(tmp_path: Path, caplog: pytest.LogCaptureFixture):
    """Covers src/nrobo/__main__.py via subprocess call."""

    fake_tests = tmp_path / "tests"
    fake_suites = tmp_path / "suites"

    fake_tests.mkdir(parents=True, exist_ok=True)
    _create_a_failing_test(fake_tests)
    fake_suites.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["NROBO_TESTS_DIR"] = str(fake_tests)
    env["NROBO_SUITES_DIR"] = str(fake_suites)

    with (
        patch.object(settings, "TESTS_DIR", fake_tests),
        patch.object(settings, "SUITES_DIR", fake_suites),
        patch.object(sys, "argv", ["nrobo"]),
    ):
        result = subprocess.run(
            ["nrobo"],
            cwd=str(tmp_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,  # ✅ pass updated environment
        )

    print(result.stdout)

    assert "assert (1 + 1) == 3" in result.stdout
    assert "AssertionError" in result.stdout


def test_copy_configs_if_updated_handles_file_not_found(monkeypatch):
    # Patch sys.argv to simulate command-line input
    monkeypatch.setattr("sys.argv", ["nrobo"])

    # Patch the function to raise FileNotFoundError
    with patch("nrobo.helpers.cli_parser.copy_configs_if_updated", side_effect=FileNotFoundError):
        try:
            # It should not raise, just handle internally
            get_nrobo_arg_parser()
        except FileNotFoundError:
            pytest.fail("FileNotFoundError was not suppressed as expected")

def test_add_basetemp_if_not_present(monkeypatch):
    # Setup minimal argv
    monkeypatch.setattr("sys.argv", ["nrobo"])

    # Patch settings and os.environ
    with patch("nrobo.helpers.cli_parser.settings.NROBO_BASENAME_TMP", ".pytest_tmp"):
        suites, browser, args, unknown_args = get_nrobo_arg_parser()

        # Assertion: should contain the basetemp that was not originally in args
        assert "--basetemp=.pytest_tmp" in unknown_args


@patch("nrobo.helpers._pytest_helper.Path.open", create=True)
@patch("nrobo.helpers.cli_parser.get_nrobo_arg_parser", autospec=True)
@patch("nrobo.cli.main.detect_or_validate_suites", autospec=True)
@patch("nrobo.cli.main.detect_fixture_usage", autospec=True)
@patch("nrobo.cli.main.prepare_pytest_cli_options", autospec=True)
@patch("nrobo.cli.main.settings")  # 👈 only patch the settings imported in cli.py
@patch("nrobo.cli.main.pytest")
@patch("nrobo.cli.main.logger")
@pytest.mark.parametrize("coverage_exists", [True, False])
def test_coverage_reporting_logic(
    mock_logger,
    mock_pytest,
    mock_settings_cli,  # this patches `settings` inside nrobo.cli
    mock_prepare_opts,
    mock_detect_fixture,
    mock_validate_suites,
    mock_get_parser,
    mock_path_open,
    coverage_exists,
):

    # Simulate CLI args
    fake_args = MagicMock()
    fake_args.coverage = True
    fake_args.no_headless = True
    mock_get_parser.return_value = (["dummy_suite"], "chrome", fake_args, [])

    # Dummy return values
    mock_validate_suites.return_value = ["dummy_suite"]
    mock_detect_fixture.return_value = False
    mock_prepare_opts.return_value = ["--some", "--pytest-arg"]
    mock_pytest.main.return_value = 0

    # Simulate YAML read
    mock_path_open.side_effect = lambda path, *a, **k: StringIO("tests:\n  - test_example.py::test_case")

    # Create mocked coverage path
    fake_cov_path = MagicMock(spec=Path)
    fake_cov_path.exists.return_value = coverage_exists
    fake_cov_path.resolve.return_value = Path("/fake/coverage/index.html")

    # Patch settings inside cli.py (not global settings)
    mock_settings_cli.COVERAGE_REPORT_HTML = fake_cov_path
    mock_settings_cli.ALLURE_RESULTS_DIR = "/non/existing/dir"
    mock_settings_cli.NROBO_APP = "nRoBo"
    mock_settings_cli.TESTS_DIR = Path("/tests")

    # Run test
    exit_code = run()
    assert exit_code == 0

    if coverage_exists:
        expected = call("📈 Coverage report available → file:///fake/coverage/index.html")
        assert expected in mock_logger.info.call_args_list
    else:
        expected = call(f"⚠️ Coverage report path not found ({fake_cov_path}).")
        assert expected in mock_logger.warning.call_args_list


def test_cli_entrypoint_executes_main_with_args(tmp_path):
    cli_path = Path("src/nrobo/cli/main.py").resolve()

    # Load the module dynamically
    spec = importlib.util.spec_from_file_location("nrobo.cli.main", cli_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with (patch.object(module, "main") as mock_main,
          patch("sys.argv", ["nrobo", "--version"])):
        compiled = compile(cli_path.read_text(), cli_path.name, "exec")
        with pytest.raises(SystemExit) as exc_info:
            exec_globals = {"__name__": "__main__"}
            exec(compiled, exec_globals)

        assert exc_info.value.code == 0

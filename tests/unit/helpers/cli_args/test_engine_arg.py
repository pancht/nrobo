import sys

import pytest

from nrobo.core.constants import Engines
from nrobo.helpers.cli_parser import get_nrobo_arg_parser


@pytest.fixture
def base_argv(monkeypatch):
    """
    Provide a clean sys.argv baseline for CLI tests.
    """
    argv = ["nrobo"]
    monkeypatch.setattr(sys, "argv", argv)
    return argv


def test_default_engine_is_selenium(base_argv):
    """
    By default, engine should be selenium
    and NOT forwarded to pytest args.
    """
    base_argv.extend(["--suite", "sample.yaml"])

    suites, browser, args, pytest_args = get_nrobo_arg_parser()

    assert args.engine == Engines.SELENIUM
    assert "--engine=selenium" not in pytest_args


def test_engine_playwright_is_parsed_correctly(base_argv):
    """
    Explicit --engine=playwright should be parsed correctly.
    """
    base_argv.extend(["--suite", "sample.yaml", "--engine", "playwright"])

    suites, browser, args, pytest_args = get_nrobo_arg_parser()

    assert args.engine == Engines.PLAYWRIGHT


def test_engine_playwright_is_forwarded_to_pytest_args(base_argv):
    """
    Playwright engine must be injected into pytest args.
    """
    base_argv.extend(["--suite", "sample.yaml", "--engine", "playwright"])

    suites, browser, args, pytest_args = get_nrobo_arg_parser()

    assert pytest_args[0] == "--engine=playwright"
    assert "--engine=playwright" in pytest_args


def test_engine_selenium_is_not_forwarded_to_pytest_args(base_argv):
    """
    Selenium is default and should NOT be injected
    into pytest args.
    """
    base_argv.extend(["--suite", "sample.yaml", "--engine", "selenium"])

    suites, browser, args, pytest_args = get_nrobo_arg_parser()

    assert args.engine == Engines.SELENIUM
    assert "--engine=selenium" not in pytest_args


def test_invalid_engine_is_rejected_by_argparse(base_argv):
    """
    Invalid engine values should be rejected by argparse.
    """
    base_argv.extend(["--suite", "sample.yaml", "--engine", "invalid"])

    with pytest.raises(SystemExit):
        get_nrobo_arg_parser()


def test_engine_playwright_with_existing_pytest_args(base_argv):
    base_argv.extend(
        [
            "--suite",
            "sample.yaml",
            "--engine",
            "playwright",
            "-k",
            "login",
        ]
    )

    _, _, _, pytest_args = get_nrobo_arg_parser()

    assert pytest_args[0] == "--engine=playwright"
    assert "-k" in pytest_args

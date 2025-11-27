import os
import sys
from unittest import mock

from nrobo.core import settings
from nrobo.helpers.cli_parser import get_nrobo_arg_parser


def test_cli_parses_nrobo_switches_correctly_with_minimal_args(logger):
    test_argv = [
        "nrobo",
    ]

    with mock.patch.object(sys, "argv", test_argv):
        suites, browser, args, pytest_args = get_nrobo_arg_parser()

    logger.debug(f"suites={suites}\nbrowser={browser}\n" f"args={args}\npytest_args={pytest_args}")

    assert suites is None
    assert browser == "chrome"
    assert os.getenv("NROBO_BROWSER") == "chrome"
    assert args.cov is False
    assert args.debug is False
    assert args.init is False
    assert args.no_headless is False
    assert os.getenv("NROBO_HEADLESS").lower() == "true"

    # test if debug switch sets correct values
    assert os.getenv("NROBO_DEBUG") == "False"
    assert settings.DEBUG is False

    # test if reporting param set correctly
    assert "--html=reports/report.html" in pytest_args
    assert "--self-contained-html" in pytest_args
    assert "--alluredir=allure-results" in pytest_args
    assert "--basetemp=.pytest_tmp" in pytest_args


def test_cli_parses_all_nrobo_switches_and_sets_env_and_pytest_args():
    test_argv = [
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
    ]

    with mock.patch.object(sys, "argv", test_argv):
        suites, browser, args, pytest_args = get_nrobo_arg_parser()

    print(f"suites={suites}\nbrowser={browser}\n" f"args={args}\npytest_args={pytest_args}")

    assert suites == ["suite1.yml", "suite2.yml"]

    assert browser == "chrome"
    assert os.getenv("NROBO_BROWSER") == "chrome"
    assert args.debug is True
    assert args.init is False
    assert args.cov is True
    assert args.no_headless is True
    assert os.getenv("NROBO_HEADLESS").lower() == "false"

    # test if debug switch sets correct values
    assert os.getenv("NROBO_DEBUG") == "True"
    assert settings.DEBUG is True

    # test if cov params set correctly
    assert "--cov=nrobo" in pytest_args
    assert "--cov-report=html" in pytest_args
    assert "--cov-report=term-missing" in pytest_args
    assert "--cov-fail-under=90" in pytest_args

    # test if reporting param set correctly
    assert "--html=reports/myreport.html" in pytest_args
    assert "--alluredir=allure-results/myreport.html" in pytest_args
    assert "--basetemp=.pytest_tmp" in pytest_args

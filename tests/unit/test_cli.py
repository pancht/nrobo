import os
import sys
from logging import Logger
from pathlib import Path
from unittest import mock
from unittest.mock import patch

import pytest

from nrobo.core import settings
from nrobo.core.exceptions import NoTestsFoundException
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

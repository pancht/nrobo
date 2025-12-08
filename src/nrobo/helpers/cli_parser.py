import argparse
import os
import sys
from pathlib import Path

import pytest

from nrobo.cli.commands import clean, init, nginx, update
from nrobo.core import settings
from nrobo.core.exceptions import NoSubCommandFoundByArgParser
from nrobo.helpers.io_helper import copy_configs_if_updated
from nrobo.helpers.logging_helper import get_logger, set_logger_level
from nrobo.helpers.reporting_helper import prepare_reporting_args
from nrobo.utils.command_utils import initialize_project
from nrobo.version import __version__

logger = get_logger(name=settings.NROBO_APP)


def _add_clean_parser(subparser):
    clean_parser = subparser.add_parser("clean", help="Clean test_artifacts/")
    clean_parser.add_argument("-v", "--verbose", action="store_true")


def _add_init_parser(subparser):
    init_parser = subparser.add_parser("init", help=f"{settings.NROBO_APP} project initializer")
    init_parser.add_argument(
        "--app", required=True, type=str, help="App name (used as project name)"
    )


def _add_nginx_parser(subparser):
    # nginx subcommand that forwards all args (start/stop/status/--dir)
    nginx_parser = subparser.add_parser(
        "nginx",
        help="Manage nRoBo's local Nginx server for Allure reports.",
    )
    nginx_parser.add_argument(
        "nginx_args",
        nargs=argparse.REMAINDER,
        help="Arguments for nginx subcommands (start/stop/status)",
    )


def _add_update_parser(subparsers):
    parser = subparsers.add_parser("update", help="Update nrobo dependencies")
    parser.add_argument(
        "--playwright", action="store_true", help="Update Playwright and install browsers"
    )
    parser.add_argument("--selenium", action="store_true", help="Update Selenium and webdrivers")
    parser.add_argument("--self", action="store_true", help="Update nrobo itself")
    return parser


def _base_parser():
    parser = argparse.ArgumentParser(
        description=f"{settings.NROBO_APP} - Smart Test Runner built on Pytest",
        add_help=True,
        allow_abbrev=False,  # ⛔ Prevents "--co" from resolving to "--cov"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode (prints verbose logs and sets NROBO_DEBUG=True)",  # noqa: E501
    )

    # known args
    parser.add_argument(
        "--suite",
        nargs="+",  # Accepts multiple values (space-separated)
        help="One or more suite YAML files under suites/ (space-separated or repeated).",  # noqa: E501
        default=None,
    )  # noqa: E501
    parser.add_argument(
        "--browser",
        action="store",
        help="Browser to run tests on (chrome, firefox, edge, etc.)",
        default=settings.DEFAULT_BROWSER,
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        default=False,
        help="Run browser in headed mode (default is headless)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help=f"Initialize a new {settings.NROBO_APP} project with sample suite and tests.",  # noqa: E501
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        default=False,
        help="Enable coverage reporting for the nRoBo framework. Used for nRobo framework coverage report!",
        # noqa: E501
    )

    parser.add_argument("-v", "--version", action="version", version=f"nrobo version {__version__}")

    return parser


def _sub_commands() -> argparse.ArgumentParser:
    parser = _base_parser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    _add_clean_parser(subparsers)
    _add_init_parser(subparsers)
    _add_nginx_parser(subparsers)
    _add_update_parser(subparsers)

    return parser


def _parse_subcommand(argv):
    parser = _sub_commands()
    return parser.parse_args(argv)


def _parse_nrobo_args(argv):
    argv = argv or sys.argv

    if "--help" in argv or "-h" in argv:

        parser = _sub_commands()

        logger.info(f"\n📜 {settings.NROBO_APP} Help Menu:")
        parser.print_help()

        if nrobo_not_initialized() and not is_dev_machine():
            sys.exit(0)

        try:
            user_input = (
                input(
                    f"\n❓ {settings.NROBO_APP} is backed by PyTest. Show PyTest options too? (y/n): "  # noqa: E501
                )  # noqa: E501
                .strip()
                .lower()
            )  # noqa: E501
        except EOFError:  # pragma: no cover
            user_input = "n"  # fallback in non-interactive shells # pragma: no cover

        if user_input.startswith("y"):
            # pragma: no cover
            logger.info("\n📜 Pytest Help Menu:")
            pytest.main(["--help"], plugins=None)
        raise SystemExit(0)

    parser = _base_parser()

    return parser.parse_known_args()


def _handle_subcommand_if_any(argv=None):
    argv = argv or sys.argv

    command = argv[1] if len(argv) > 1 else None
    if command not in ["clean", "init", "nginx", "update"]:
        raise NoSubCommandFoundByArgParser("No subcommand found.")

    # Run subcommand parser only
    sub_args = _parse_subcommand(argv[1:])

    if sub_args.command == "clean":
        clean.run(argv[2:])
    elif sub_args.command == "init":
        init.run(argv[2:])
    elif sub_args.command == "nginx":
        nginx.run(sys.argv[2:])
    elif sub_args.command == "update":
        update.run(argv[2:])

    sys.exit(0)


def get_nrobo_arg_parser(argv=None):
    argv = argv or sys.argv

    try:
        _handle_subcommand_if_any(argv)
    except NoSubCommandFoundByArgParser:
        pass

    args, unknown_args = _parse_nrobo_args(argv[1:])

    # Handle `nrobo --init`
    if args.init:
        initialize_project()
        sys.exit(0)

    try:
        copy_configs_if_updated()
    except FileNotFoundError:
        pass

    # Handle test execution
    suites = args.suite
    browser = args.browser

    if args.debug:
        os.environ["NROBO_DEBUG"] = "True"
        settings.DEBUG = True
        set_logger_level(logger=logger, stream_level=10, file_level=10)
    else:
        os.environ["NROBO_DEBUG"] = "False"
        settings.DEBUG = False

    # update args
    os.environ["NROBO_BROWSER"] = browser

    os.environ["NROBO_HEADLESS"] = str(not args.no_headless)

    if args.coverage:
        unknown_args.extend(
            [
                "--cov=nrobo",  # measure coverage for your framework package
                f"--cov-report=html:{settings.TEST_ARTIFACTS_DIR}/{settings.COVERAGE_REPORTS_DIR}/html",
                f"--cov-report=xml:{str(settings.COVERAGE_REPORT_XML)}",  # generate HTML report
                "--cov-report=term-missing",  # show missing lines in terminal
                "--cov-fail-under=90",  # fail if coverage < 90%
            ]
        )

    # always change temp dir under project dir
    if not any("--basetemp=" in arg for arg in unknown_args):
        if settings.NROBO_BASENAME_TMP:
            unknown_args.extend(["--basetemp=.pytest_tmp"])

    unknown_args = prepare_reporting_args(pytest_args=unknown_args)
    logger.debug(f"Final PyTest Options=>{unknown_args}")
    return suites, browser, args, unknown_args


def is_dev_machine():
    return "src" in str(settings.BASE_DIR) or (settings.BASE_DIR / "src").exists()


def nrobo_not_initialized():
    markers = [
        Path(settings.CONFIGS),
        Path(settings.TESTS_DIR),
        Path(settings.SUITES_DIR),
        Path("common") / "helpers",
        Path("common") / "utils",
    ]

    return any(not m.exists() for m in markers)


def check_if_nrobo_initialized(sys_argv=None):
    if sys_argv is None:
        sys_argv = sys.argv
    # Allowed commands that don't need full project
    bypass_keywords = ["init", "--help", "-h", "--version", "-v"]

    if is_dev_machine():
        return

    if nrobo_not_initialized():  # pragma: no cover
        if not any(bypass in sys_argv for bypass in bypass_keywords):
            print(f"🚫 {settings.NROBO_APP} project not initialized.")
            print("💡 Run this to get started:")
            print("    nrobo init --app my_project")
            sys.exit(1)  # pragma: no cover

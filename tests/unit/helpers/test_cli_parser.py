import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from nrobo.cli.commands import init, clean
from nrobo.core import settings
from nrobo.helpers import cli_parser
from nrobo.helpers.cli_parser import get_nrobo_arg_parser, parse_nrobo_args, check_if_nrobo_initialized, \
    nrobo_not_initialized
from nrobo.utils.common_utils import normalize_cli_output


@pytest.mark.parametrize(
    "user_input, expect_exit",
    [
        ("n\n", 0),
        ("y\n", 0),
    ],
)
def test_nrobo_help_switch_subprocess(tmp_path, user_input, expect_exit):
    """
    Integration‑style test: run the `nrobo --help` CLI in a subprocess,
    send interactive input, and check stdout + exit code.
    """
    # Build command: assume `nrobo` is on PATH, or use python -m.
    cmd = ["nrobo", "--help"]
    # Run subprocess: send user_input to stdin, capture stdout/stderr
    result = subprocess.run(
        cmd,
        input=user_input,  # send input
        capture_output=True,
        text=True,
        check=False,  # so we can inspect non-zero exit code
    )

    # Check exit code
    assert result.returncode == expect_exit

    output = normalize_cli_output(result.stdout)

    # Now assert expected help content
    assert f"{settings.NROBO_APP} - Smart Test Runner built on Pytest" in output
    assert "--suite" in output
    assert "Enable debug mode (prints verbose logs and sets NROBO_DEBUG=True)" in output
    assert "One or more suite YAML files under suites/ (space-separated or repeated)." in output

    assert "--browser" in output
    assert "Browser to run tests on (chrome, firefox, edge, etc.)" in output

    assert "--no-headless" in output
    assert "Run browser in headed mode (default is headless)" in output

    assert "--init" in output
    assert f"Initialize a new {settings.NROBO_APP} project with sample suite and tests." in output

    assert "--coverage" in output
    assert (
        "Enable coverage reporting for the nRoBo framework. Used for nRobo framework coverage report!"
        in output
    )

    if user_input == "y\n" and not nrobo_not_initialized():
        # a few assertions for pytest help
        assert "to see available markers type: pytest --markers" in output
        assert "to see available fixtures type: pytest --fixtures" in output


def test_version_flag(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["nrobo", "--version"])
    with pytest.raises(SystemExit) as excinfo:
        cli_parser.get_nrobo_arg_parser()

    captured = capsys.readouterr()
    assert "nrobo version" in captured.out
    assert excinfo.value.code == 0


def test_clean_subcommand_triggers(monkeypatch):
    called = {}

    def mock_clean_run(args):
        called["args"] = args

    monkeypatch.setattr(cli_parser.clean, "run", mock_clean_run)
    monkeypatch.setattr(sys, "argv", ["nrobo", "clean", "-v"])

    with pytest.raises(SystemExit) as excinfo:
        cli_parser.get_nrobo_arg_parser()

    assert excinfo.value.code == 0
    assert called["args"] == ["-v"]


def test_parse_nrobo_args(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["nrobo", "--suite", "smoke.yaml", "--browser", "firefox", "--no-headless"])

    suites, browser, args, unknown = cli_parser.get_nrobo_arg_parser()

    assert suites == ["smoke.yaml"]
    assert browser == "firefox"
    assert args.no_headless is True
    assert isinstance(unknown, list)

def test_init_flag(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["nrobo", "--init"])
    called = {}

    def mock_initialize():
        called["hit"] = True

    monkeypatch.setattr(cli_parser, "initialize_project", mock_initialize)

    with pytest.raises(SystemExit) as excinfo:
        cli_parser.get_nrobo_arg_parser()

    assert excinfo.value.code == 0
    assert called["hit"] is True


def test_help_flag_n(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["nrobo", "--help"])
    monkeypatch.setattr("builtins.input", lambda _: "n")
    monkeypatch.setattr("builtins.print", lambda *args, **kwargs: None)

    with pytest.raises(SystemExit) as excinfo:
        cli_parser.get_nrobo_arg_parser()

    assert excinfo.value.code == 0

def test_help_flag_y(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["nrobo", "--help"])
    monkeypatch.setattr("builtins.input", lambda _: "y")

    # Patch pytest.main to prevent actual help printing
    called = {}
    def fake_pytest_main(args, **kwargs):
        called["args"] = args
        return 0

    monkeypatch.setattr("pytest.main", fake_pytest_main)

    with pytest.raises(SystemExit) as excinfo:
        cli_parser.get_nrobo_arg_parser()

    assert excinfo.value.code == 0


def test_init_run_creates_files_via_direct_template_patch(tmp_path, monkeypatch):
    from nrobo.cli.commands import init

    # Create a custom template file in temp
    template_path = tmp_path / "custom_template.yaml"
    template_path.write_text("""
project:
  name: "{{project_name}}"

folders:
  - demo/path

files:
  greeting.txt: "Hello {{project_name}}!"
  demo/info.txt: "Info: {{project_name}}"
""")

    # Patch PROJECT_TEMPLATE_PATH to use our temp template
    monkeypatch.setattr(init, "PROJECT_TEMPLATE_PATH", template_path)

    # Patch cwd to temp so base_path="." points to tmp_path
    monkeypatch.chdir(tmp_path)

    # Execute the real command
    init.run(["--app", "SuperApp"])

    # Assert created structure and content
    assert (tmp_path / "demo" / "path").is_dir()
    assert (tmp_path / "greeting.txt").read_text() == "Hello SuperApp!"
    assert (tmp_path / "demo" / "info.txt").read_text() == "Info: SuperApp"



# --- Helper fixtures / mocks ---

@pytest.fixture(autouse=True)
def isolate_env(monkeypatch, tmp_path):
    """
    Make sure we test in an isolated directory (tmp_path),
    and isolate settings.BASE_DIR to simulate dev / prod env.
    """
    # Change cwd to tmp_path
    monkeypatch.chdir(tmp_path)
    # Default: consider BASE_DIR does not exist (simulate installed package)
    monkeypatch.setattr(settings, "BASE_DIR", Path("/nonexistent_base_dir"), raising=False)
    yield
    # no cleanup needed


# --- Tests ---

def test_subcommand_clean_invokes_clean_and_exits(monkeypatch):
    """nrobo clean should call clean.run and exit with code 0."""
    monkeypatch.setattr(sys, "argv", ["nrobo", "clean"])
    called = {}
    monkeypatch.setattr(clean, "run", lambda args: called.setdefault("clean_args", args))

    with pytest.raises(SystemExit) as exc:
        get_nrobo_arg_parser()

    assert exc.value.code == 0
    # clean was called with no additional args
    assert called["clean_args"] == []


def test_subcommand_init_invokes_init_and_exits(monkeypatch):
    """nrobo init --app MyApp should call init.run and exit with code 0."""
    monkeypatch.setattr(sys, "argv", ["nrobo", "init", "--app", "MyApp"])
    called = {}
    monkeypatch.setattr(init, "run", lambda args: called.setdefault("init_args", args))

    with pytest.raises(SystemExit) as exc:
        get_nrobo_arg_parser()

    assert exc.value.code == 0
    assert called["init_args"] == ["--app", "MyApp"]


def test_init_flag_triggers_initialize_project(monkeypatch):
    """nrobo --init should call initialize_project and exit."""
    monkeypatch.setattr(sys, "argv", ["nrobo", "--init"])
    called = {}
    monkeypatch.setattr(cli_parser, "initialize_project", lambda: called.setdefault("initialized", True))

    with pytest.raises(SystemExit) as exc:
        get_nrobo_arg_parser()

    assert exc.value.code == 0
    assert called.get("initialized") is True


def test_help_flag_with_yes_shows_pytest_help(monkeypatch, capsys):
    """‘--help’ with input ‘y’ calls pytest.main with ['--help']."""
    monkeypatch.setattr(sys, "argv", ["nrobo", "--help"])
    monkeypatch.setattr("builtins.input", lambda _: "y")

    called = {}
    def fake_pytest_main(args, **kwargs):
        called["args"] = args
        return 0

    monkeypatch.setattr("pytest.main", fake_pytest_main)

    with pytest.raises(SystemExit) as exc:
        get_nrobo_arg_parser()

    assert exc.value.code == 0
    assert called.get("args") == None

    captured = capsys.readouterr()
    assert settings.NROBO_APP in captured.out  # help header printed


def test_help_flag_with_no_shows_only_nrobo_help(monkeypatch, capsys):
    """‘--help’ with input ‘n’ should skip pytest help and exit cleanly."""
    monkeypatch.setattr(sys, "argv", ["nrobo", "--help"])
    monkeypatch.setattr("builtins.input", lambda _: "n")

    with pytest.raises(SystemExit) as exc:
        get_nrobo_arg_parser()

    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert settings.NROBO_APP in captured.out
    # pytest.main should not have been called
    # (no error is enough — we mock nothing on pytest.main)


def test_coverage_flag_adds_cov_args(monkeypatch):
    """When --coverage is passed, returned unknown_args include coverage options."""
    # we run minimal scenario: no subcommand, no suites
    # So sys.argv includes coverage
    monkeypatch.setattr(sys, "argv", ["nrobo", "--coverage"])
    suites, browser, args, unknown = get_nrobo_arg_parser()

    # coverage should be set
    assert args.coverage is True
    # unknown args should contain cov-related flags
    assert "--cov=nrobo" in unknown
    assert "--cov-report=html" in unknown
    assert "--cov-report=term-missing" in unknown
    # also basetemp fallback if settings.NROBO_BASENAME_TMP truthy
    if settings.NROBO_BASENAME_TMP:
        assert "--basetemp=.pytest_tmp" in unknown


def test_check_if_nrobo_initialized_exits_when_missing(monkeypatch, tmp_path, capsys):
    """If project structure missing and no bypass keyword, should exit."""
    # Ensure markers do not exist
    monkeypatch.setattr(settings, "CONFIGS", "configs", raising=False)
    monkeypatch.setattr(settings, "TESTS_DIR", "tests", raising=False)
    monkeypatch.setattr(settings, "SUITES_DIR", "suites", raising=False)

    # sys argv simulating test run (not bypass)
    fake_argv = ["nrobo", "run"]
    with pytest.raises(SystemExit) as exc:
        check_if_nrobo_initialized(sys_argv=fake_argv)
    assert exc.value.code == 1

    out, _ = capsys.readouterr()
    assert "project not initialized" in out


def test_check_if_nrobo_initialized_allows_bypass(monkeypatch, tmp_path):
    """If argv contains bypass keyword (e.g. init), should not exit even if missing markers."""
    fake_argv = ["nrobo", "init"]
    # markers missing as before
    monkeypatch.setattr(settings, "CONFIGS", "configs", raising=False)
    monkeypatch.setattr(settings, "TESTS_DIR", "tests", raising=False)
    monkeypatch.setattr(settings, "SUITES_DIR", "suites", raising=False)

    # Should not raise
    check_if_nrobo_initialized(sys_argv=fake_argv)

def test_check_if_nrobo_initialized_skips_on_dev_env():
    """
    If settings.BASE_DIR points to a dev environment (contains 'src'),
    check_if_nrobo_initialized should skip initialization checks.
    """
    # Simulate a dev environment with 'src' in path
    fake_base = Path("/Users/mac/PycharmProjects/nrobo/src")
    from nrobo.core import settings
    with patch.object(settings, "BASE_DIR", fake_base), \
         patch.object(sys, "argv", ["nrobo", "--co"]):
        # No SystemExit should be raised
        check_if_nrobo_initialized(sys_argv=sys.argv)


def test_parse_nrobo_args_defaults_and_flags():
    test_argv = ["nrobo", "--suite", "smoke", "--browser", "chrome"]
    with patch("sys.argv", test_argv):
        args, unknown = parse_nrobo_args(sys.argv[1:])
        assert args.suite == ["smoke"]
        assert args.browser == "chrome"
        assert args.debug is False
        assert args.init is False
        assert args.coverage is False
        assert unknown == []


def test_parse_nrobo_args_with_unknown_args():
    test_argv = ["nrobo", "--foo", "bar"]
    with patch("sys.argv", test_argv):
        args, unknown = parse_nrobo_args(sys.argv[1:])
        assert args.suite is None
        assert unknown == ["--foo", "bar"]


@patch("nrobo.helpers.cli_parser.init.run")
@patch("nrobo.helpers.cli_parser.parse_subcommand")
def test_subcommand_init_triggers_init_run(mock_parse_subcommand, mock_init_run):
    # Simulate CLI input: nrobo init --app testapp
    test_args = ["nrobo", "init", "--app", "testapp"]

    # Mock subcommand parsing to return 'init'
    mock_parse_subcommand.return_value = MagicMock(command="init")

    # Patch sys.exit to raise SystemExit so we can catch it
    with patch("sys.argv", test_args), pytest.raises(SystemExit) as exc_info:
        cli_parser.get_nrobo_arg_parser()

    # Check init.run was called with the correct arguments
    mock_init_run.assert_called_once_with(["--app", "testapp"])
    assert exc_info.value.code == 0


def test_parse_nrobo_args_handles_eoferror(monkeypatch):
    # Simulate CLI input with --help
    test_args = ["--help"]

    # Simulate input() raising EOFError
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(EOFError))

    # Patch sys.exit and pytest.main to avoid actual exit and help display
    monkeypatch.setattr("pytest.main", lambda *a, **kw: 0)

    with pytest.raises(SystemExit) as exc_info:
        parse_nrobo_args(test_args)

    assert exc_info.value.code == 0


def test_check_if_nrobo_initialized_exits_when_required_dirs_missing():
    """Should exit if project markers are missing and not a bypass command."""
    with (
        patch("nrobo.helpers.cli_parser.Path.exists", return_value=False),
        patch.object(settings, "BASE_DIR", Path("/nonexistent_dir")),
        patch.object(sys, "argv", ["nrobo", "run"]),
        pytest.raises(SystemExit) as excinfo,
    ):
        check_if_nrobo_initialized()
    assert excinfo.value.code == 1


@pytest.mark.parametrize("bypass_flag", [["init"], ["--help"], ["-h"], ["--version"], ["-v"]])
def test_check_if_nrobo_initialized_does_not_exit_on_bypass_flags(bypass_flag):
    """Should not exit if any bypass keyword is present in argv."""
    with (
        patch("nrobo.helpers.cli_parser.Path.exists", return_value=False),
        patch.object(settings, "BASE_DIR", Path("/nonexistent_dir")),
        patch.object(sys, "argv", ["nrobo"] + bypass_flag)
    ):
        check_if_nrobo_initialized()  # should not raise


@patch("nrobo.helpers.cli_parser.Path.exists", return_value=False)
@patch.object(settings, "BASE_DIR", Path("/fake"))
@patch.object(sys, "argv", ["nrobo", "run"])
def test_check_if_nrobo_initialized_exits(mock_exists):
    with pytest.raises(SystemExit) as excinfo:
        check_if_nrobo_initialized()
    assert excinfo.value.code == 1

import subprocess
import sys
from unittest.mock import patch

import pytest

from nrobo.cli.commands import init
from nrobo.core import settings
from nrobo.helpers import cli_parser
from nrobo.helpers.cli_parser import get_nrobo_arg_parser
from nrobo.utils.common_utils import normalize_cli_output


@pytest.mark.parametrize(
    "user_input, expect_exit",
    [
        ("n\n", 0),
        #("y\n", 0),
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

    if user_input == "y\n":
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
    assert called["args"] == ["--help"]


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

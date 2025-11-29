import sys

import pytest

from nrobo.core import settings
from nrobo.helpers.cli_parser import get_nrobo_arg_parser


@pytest.mark.parametrize(
    "user_input, expect_exit",
    [
        ("n", True),
        ("y", True),
    ],
)
def test_get_nrobo_arg_parser_help_switch(monkeypatch, capsys, user_input, expect_exit):
    """
    Simulate `nrobo --help` and check that help message is printed
    and when user inputs 'y', pytest help is printed and exit occurs.
    """

    # Build argv as if user passed --help
    monkeypatch.setattr(sys, "argv", ["nrobo", "--help"])

    # Patch input() to return user_input, to simulate interactive reply
    monkeypatch.setitem(sys.modules, "builtins", __import__("builtins"))
    monkeypatch.setattr("builtins.input", lambda prompt="": user_input)

    if expect_exit:
        with pytest.raises(SystemExit) as exc:
            get_nrobo_arg_parser()
        # Optionally assert exit code is zero
        assert exc.value.code == 0
    else:
        # Should not exit — get parser tuple
        suites, browser, args, pytest_args = get_nrobo_arg_parser()
        # Since help was asked and user answered 'n', nothing else should be parsed
        assert args is not None
        assert "--help" not in pytest_args

    captured = capsys.readouterr()

    # Assert help messages
    assert f"{settings.APP} - Smart Test Runner built on Pytest" in captured.out
    assert "Enable debug mode (prints verbose logs and sets NROBO_DEBUG=True)" in captured.out
    assert (
        "One or more suite YAML files under suites/ (space-separated or repeated)." in captured.out
    )
    assert "Browser to run tests on (chrome, firefox, edge, etc.)" in captured.out
    assert "Run browser in headed mode (default is headless)" in captured.out
    assert f"Initialize a new {settings.APP} project with sample suite and tests." in captured.out
    assert (
        "Enable coverage reporting for the nRoBo framework. Used for nRobo framework coverage report!"
        in captured.out
    )

    if user_input == "y":
        assert "--co" in captured.out
        assert "--collect-only" in captured.out
        assert "Reporting:" in captured.out
        assert "to see available fixtures type: pytest --fixtures" in captured.out

from unittest.mock import patch

import pytest

from nrobo.cli.commands import generate


def test_generate_page_invokes_generator(monkeypatch):
    """
    Test that 'nrobo generate page <PageName>' correctly calls generate_page_file
    with the provided page name.
    """
    with patch("nrobo.cli.commands.generate.generate_page_file") as mock_generate:
        args = ["page", "LoginPage"]
        generate.run(args)

        mock_generate.assert_called_once_with("LoginPage")


def test_generate_page_shows_help_when_missing_args(capsys):
    """
    Test that help message is shown when required arguments are missing.
    """
    with pytest.raises(SystemExit):
        generate.run([])

    out, err = capsys.readouterr()
    assert "usage:" in out or "usage:" in err
    assert (
        "nrobo: error: the following arguments are required: page, name" in out
        or "nrobo: error: the following arguments are required: page, name" in err
    )


def test_generate_page_help_output(capsys):
    """
    Test that running with --help prints the expected help text.
    """
    with pytest.raises(SystemExit):  # argparse exits after showing help
        generate.run(["--help"])

    out, err = capsys.readouterr()
    assert "Generate nRobo components" in out or "Generate nRobo components" in err
    assert "Page Object class" in out or "Page Object class" in err

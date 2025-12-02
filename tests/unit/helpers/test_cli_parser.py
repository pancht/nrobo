import subprocess
import sys

import pytest

from nrobo.core import settings
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

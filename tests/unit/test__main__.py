import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from nrobo.core import settings
from nrobo.helpers.test_helper import _create_a_passing_test


def test___main___invokes_cli_main(tmp_path: Path):
    """Covers src/nrobo/__main__.py via subprocess call."""

    fake_tests = tmp_path / "tests"
    fake_suites = tmp_path / "suites"

    _create_a_passing_test(fake_tests)
    fake_suites.mkdir()

    with (
        patch.object(settings, "TESTS_DIR", fake_tests),
        patch.object(settings, "SUITES_DIR", fake_suites),
        patch.object(sys, "argv", ["nrobo", str(fake_tests)]),
    ):
        subprocess.run(
            ["coverage", "run", "-m", "src/nrobo/cli/main.py"],
            cwd="src",  # 👈 critical to run from correct package root
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

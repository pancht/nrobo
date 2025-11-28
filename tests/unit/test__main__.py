import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch

from nrobo.core import settings


def _create_sample_test(test_dir: Path):
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "test_sample.py").write_text(
        textwrap.dedent(
            """
        def test_addition():
            assert 1 + 1 == 2
    """
        )
    )


def test___main___invokes_cli_main(tmp_path: Path):
    """Covers src/nrobo/__main__.py via subprocess call."""

    fake_tests = tmp_path / "tests"
    fake_suites = tmp_path / "suites"

    _create_sample_test(fake_tests)
    fake_suites.mkdir()

    with (
        patch.object(settings, "TESTS_DIR", fake_tests),
        patch.object(settings, "SUITES_DIR", fake_suites),
        patch.object(sys, "argv", ["nrobo", str(fake_tests)]),
    ):
        subprocess.run(
            [sys.executable, "-m", "src/nrobo/__main__.py"],
            cwd="src",  # 👈 critical to run from correct package root
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

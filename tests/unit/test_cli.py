import subprocess
import sys
import venv
from pathlib import Path

import pytest

from nrobo.core import settings


def create_virtualenv(venv_dir: Path):
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(venv_dir)
    return venv_dir / ("Scripts" if sys.platform == "win32" else "bin")


@pytest.mark.skipif(
    sys.platform == "win32", reason="nrobo install test not validated on Windows yet"
)
def test_nrobo_installation_and_cli(tmp_path: Path):
    # Create a virtualenv
    venv_dir = tmp_path / "venv"
    bin_dir = create_virtualenv(venv_dir)

    # Install nrobo locally in the venv
    subprocess.run(
        [bin_dir / "pip", "install", "-e", "."],
        cwd=Path(__file__).parent.parent.parent,  # Root of nrobo project
        check=True,
    )

    # Run `nrobo --help` from the new venv to validate CLI entry point
    result = subprocess.run(
        [bin_dir / "nrobo", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert f"{settings.APP} - Smart Test Runner built on Pytest" in result.stdout
    assert "usage" in result.stdout

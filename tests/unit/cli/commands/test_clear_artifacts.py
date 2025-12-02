import os
import shutil
import sys

import pytest
from io import StringIO
from contextlib import redirect_stdout

from nrobo.cli.commands.clean import clean_artifacts, run

@pytest.fixture
def artifact_dir(tmp_path, monkeypatch):
    test_dir = tmp_path / "test_artifacts"
    test_dir.mkdir()
    monkeypatch.setattr("nrobo.cli.commands.clean.ARTIFACT_DIR", str(test_dir))
    return test_dir

def test_clean_artifacts_removes_all_but_gitkeep(artifact_dir, capsys):
    # Setup files
    (artifact_dir / ".gitkeep").write_text("")
    (artifact_dir / "temp.log").write_text("log data")
    (artifact_dir / "report.txt").write_text("report")

    subdir = artifact_dir / "logs"
    subdir.mkdir()
    (subdir / "junk.txt").write_text("junk")

    # Run cleanup
    clean_artifacts(verbose=True)

    # Capture output
    captured = capsys.readouterr()
    assert "Deleted file" in captured.out
    assert "cleaned" in captured.out

    # Check .gitkeep still exists
    assert (artifact_dir / ".gitkeep").exists()

    # Check other files/dirs are gone
    assert not (artifact_dir / "temp.log").exists()
    assert not (artifact_dir / "report.txt").exists()
    assert not subdir.exists()
    assert f"📂 Removed empty dir: {subdir}" in captured.out

def test_clean_artifacts_no_verbose(artifact_dir):
    # Setup a non-.gitkeep file
    (artifact_dir / "temp.json").write_text("temp")
    subdir = artifact_dir / "logs"
    subdir.mkdir()
    (subdir / "junk.txt").write_text("junk")

    # Capture stdout
    f = StringIO()
    with redirect_stdout(f):
        clean_artifacts(verbose=False)
    out = f.getvalue()
    assert "Deleted file" not in out  # no verbose logs
    assert "Removed empty dir" not in out
    assert "cleaned" in out

def test_clean_artifacts_silent_mode(artifact_dir, capsys):
    (artifact_dir / "foo.log").write_text("bar")
    logs_dir = artifact_dir / "logs"
    logs_dir.mkdir()
    (logs_dir / ".gitkeep").write_text("")  # makes dir non-empty after cleanup
    (logs_dir / "temp.txt").write_text("temp")


    # Call with verbose=False (default)
    clean_artifacts()

    captured = capsys.readouterr()
    assert "Deleted file" not in captured.out
    assert "Removed empty dir" not in captured.out
    assert "cleaned" in captured.out


def test_run_calls_clean_artifacts_verbose(monkeypatch, artifact_dir):
    (artifact_dir / "trash.txt").write_text("waste")
    monkeypatch.setattr("sys.stdout", StringIO())

    run(["--verbose"])
    output = sys.stdout.getvalue()

    assert "Deleted file:" in output
    assert "✅ test_artifacts cleaned." in output

def test_run_when_dir_missing(monkeypatch, tmp_path):
    # Simulate missing directory
    missing = tmp_path / "missing_artifacts"
    monkeypatch.setattr("nrobo.cli.commands.clean.ARTIFACT_DIR", str(missing))

    f = StringIO()
    with redirect_stdout(f):
        run([])
    out = f.getvalue()
    assert "does not exist" in out

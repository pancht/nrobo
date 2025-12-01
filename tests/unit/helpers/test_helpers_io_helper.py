import os
import time
from unittest.mock import patch

import pytest
from pathlib import Path
from nrobo.helpers.io_helper import copy_configs_if_updated, is_sync_needed


def test_is_sync_needed_when_dest_does_not_exist(tmp_path):
    source = tmp_path / "configs"
    source.mkdir()
    (source / ".env").write_text("NROBO_DEBUG=True")

    dest = tmp_path / "does_not_exist"

    assert is_sync_needed(source, dest) is True

def test_is_sync_needed_when_file_missing_in_dest(tmp_path):
    source = tmp_path / "configs"
    dest = tmp_path / "dest_configs"

    source.mkdir()
    dest.mkdir()

    (source / ".env").write_text("value")

    assert is_sync_needed(source, dest) is True

def test_is_sync_needed_when_source_is_newer(tmp_path):
    source = tmp_path / "configs"
    dest = tmp_path / "dest_configs"

    source.mkdir()
    dest.mkdir()

    src_file = source / ".env"
    dest_file = dest / ".nrobo_env"

    src_file.write_text("newer")
    dest_file.write_text("older")

    # Artificially make dest file older
    time.sleep(1)
    src_file.write_text("newest")

    assert is_sync_needed(source, dest) is True

def test_is_sync_needed_when_up_to_date(tmp_path):
    source = tmp_path / "configs"
    dest = tmp_path / "dest_configs"

    source.mkdir()
    dest.mkdir()

    file_name = ".env"
    dest_file_name = ".nrobo_env"
    content = "unchanged"

    (source / file_name).write_text(content)
    (dest / dest_file_name).write_text(content)

    # Copy timestamps
    timestamp = (source / file_name).stat().st_mtime
    os.utime(dest / dest_file_name, (timestamp, timestamp))

    assert is_sync_needed(source, dest) is False


def test_copy_configs_raises_if_source_not_found(monkeypatch, tmp_path):
    # Simulate project root as tmp_path (no 'configs/' present)
    monkeypatch.setattr(Path, "cwd", lambda: tmp_path)

    with pytest.raises(FileNotFoundError, match="Source directory not found"):
        copy_configs_if_updated()

def test_copy_configs_when_sync_needed(monkeypatch, tmp_path):
    project_root = tmp_path
    source_dir = project_root / "configs"
    dest_dir = project_root / "src" / "nrobo" / "templates" / "configs"

    # Create source config directory and sample files
    source_dir.mkdir(parents=True)
    (source_dir / ".env").write_text("NROBO_DEBUG=True")
    (source_dir / ".flake8").write_text("[flake8]")

    # Patch cwd
    monkeypatch.setattr(Path, "cwd", lambda: project_root)

    # Ensure dest doesn't exist yet (triggers copy)
    assert not dest_dir.exists()

    copy_configs_if_updated()

    # Check files copied
    assert (dest_dir / ".nrobo_env").exists()
    assert not (dest_dir / ".flake8").exists()

    assert (dest_dir / ".nrobo_env").read_text() == "NROBO_DEBUG=True"


def test_copy_configs_skips_when_not_needed(monkeypatch, tmp_path):
    source_dir = tmp_path / "configs"
    source_dir.mkdir(parents=True)
    (source_dir / ".env").write_text("mock")

    monkeypatch.setattr(Path, "cwd", lambda: tmp_path)

    with patch("nrobo.helpers.io_helper.is_sync_needed", return_value=False), \
         patch("builtins.print") as mock_print:
        copy_configs_if_updated()

        mock_print.assert_called_with("🟢 Skipped copy (configs already up to date).")
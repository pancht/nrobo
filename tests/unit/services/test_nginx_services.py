import hashlib
import os
import subprocess
from pathlib import Path

import pytest

from nrobo.services import nginx_service
from nrobo.services.nginx_service_state import clear_state, save_state, user_cache_dir


# --- Fixtures & helpers ---

@pytest.fixture(autouse=True)
def isolate_user_cache(tmp_path, monkeypatch):
    """Temporarily override user cache dir so we don't pollute real home dirs."""
    fake_cache = tmp_path / "user_cache"
    monkeypatch.setenv("XDG_CACHE_HOME", str(fake_cache))
    return fake_cache

@pytest.fixture
def dummy_allure_dir(tmp_path):
    """Create a fake directory with an index.html to simulate a valid Allure report."""
    d = tmp_path / "fake_allure"
    d.mkdir()
    (d / "index.html").write_text("<html></html>")
    return d

# --- Tests ---

def test__stable_prefix_for_dir_creates_expected_dirs(dummy_allure_dir, isolate_user_cache):
    root = dummy_allure_dir.resolve()
    prefix = nginx_service._stable_prefix_for_dir(root)
    # Expect prefix under user cache, with hashed name
    h = hashlib.sha1(root.as_posix().encode("utf-8")).hexdigest()[:10]
    expected = Path(user_cache_dir("nrobo")) / "nginx" / f"allure-{h}"
    assert prefix == expected
    assert (prefix / "conf").is_dir()
    assert (prefix / "logs").is_dir()

def test_reuse_or_launch_allure_nginx_raises_if_no_index(dummy_allure_dir):
    invalid = dummy_allure_dir / "subdir"
    invalid.mkdir()
    with pytest.raises(FileNotFoundError):
        nginx_service.reuse_or_launch_allure_nginx(str(invalid))

def test_reuse_or_launch_allure_nginx_start_invokes_nginx(monkeypatch, dummy_allure_dir, tmp_path):
    """Simulate nginx not present or fresh start — mock subprocess calls and port finding."""
    # Patch find_free_port to a fixed port
    monkeypatch.setattr(nginx_service, "find_free_port", lambda: 12345)
    # Patch which to pretend nginx exists
    monkeypatch.setattr(nginx_service, "_which", lambda cmd: "/usr/bin/nginx")
    # Patch subprocess.run to do nothing (pretend nginx start works)
    mock_run = monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess(args, 0))
    # Patch wait_until_listening to succeed immediately
    monkeypatch.setattr(nginx_service, "wait_until_listening", lambda port, host, timeout: True)

    result = nginx_service.reuse_or_launch_allure_nginx(str(dummy_allure_dir), open_browser=False)

    # Validate returned structure
    assert result["port"] == 12345
    assert result["served_dir"] == str(dummy_allure_dir.resolve())
    assert result["runtime_dir"]  # should be some cache dir
    assert result["mode"] == "user-local"
    assert "url" in result and result["url"].startswith("http://127.0.0.1:")

def test_reuse_or_launch_allure_nginx_reuse(monkeypatch, dummy_allure_dir, tmp_path):
    """Simulate previous state + pid + port free — so should reuse instead of re‑start."""
    # Setup fake state
    root = dummy_allure_dir.resolve()
    prefix = nginx_service._stable_prefix_for_dir(root)
    pid_file = prefix / "logs" / "nginx.pid"
    pid_file.write_text("9999")  # fake pid

    prev_state = {
        "served_dir": str(root),
        "runtime_dir": str(prefix),
        "port": 23456,
        "url": f"http://127.0.0.1:23456/",
    }
    save_state(prev_state)

    # Mock port check and process check
    monkeypatch.setattr(nginx_service, "is_port_in_use", lambda port, host="127.0.0.1": True)
    # Patch os.kill to raise no exception (pretend process exists)
    monkeypatch.setattr(os, "kill", lambda pid, sig: None)

    result = nginx_service.reuse_or_launch_allure_nginx(str(dummy_allure_dir), open_browser=False)

    assert result["port"] == 23456
    assert result["runtime_dir"] == str(prefix)
    assert result["served_dir"] == str(root)
    assert result["mode"] == "user-local"

    # Cleanup saved state
    clear_state()

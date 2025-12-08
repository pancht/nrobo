import argparse
import os
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nrobo.cli.commands import nginx
from nrobo.cli.commands.nginx import _pid_running, cmd_start, cmd_status, cmd_stop


@pytest.fixture
def fake_args():
    class Args:
        dir = "/tmp/fake-allure"  # nosec B108

    return Args()


def test_cmd_start_success(fake_args):
    resolved_path = str(Path(fake_args.dir).resolve())
    with patch("nrobo.cli.commands.nginx.reuse_or_launch_allure_nginx") as mock_launch:
        mock_launch.return_value = {"url": "http://localhost:8888"}
        cmd_start(fake_args)
        mock_launch.assert_called_once_with(resolved_path)


def test_cmd_start_with_invalid_path():
    args = MagicMock()
    args.dir = None
    with patch("nrobo.cli.commands.nginx.run") as mock_run, patch("sys.exit") as mock_exit:
        cmd_start(args)
        mock_run.assert_called()
        mock_exit.assert_called_once()


def test_cmd_status_with_running_nginx(tmp_path):
    # Create fake state and pid file
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (logs_dir / "nginx.pid").write_text("1234")
    state = {
        "url": "http://localhost:8888",
        "port": 8888,
        "served_dir": "/tmp",  # nosec B108
        "runtime_dir": str(tmp_path),
    }

    with (
        patch("nrobo.cli.commands.nginx.load_state", return_value=state),
        patch("nrobo.cli.commands.nginx._pid_running", return_value=True),
    ):
        cmd_status(None)


def test_cmd_status_with_no_state():
    with patch("nrobo.cli.commands.nginx.load_state", return_value=None):
        cmd_status(None)


def test_cmd_stop_success(tmp_path):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    pid_file = logs_dir / "nginx.pid"
    pid_file.write_text("1234")

    state = {
        "runtime_dir": str(tmp_path),
    }

    with (
        patch("nrobo.cli.commands.nginx.load_state", return_value=state),
        patch("nrobo.cli.commands.nginx.clear_state") as mock_clear,
        patch("os.kill") as mock_kill,
    ):
        cmd_stop(None)
        mock_kill.assert_called_once_with(1234, 15)
        mock_clear.assert_called_once()


def test_cmd_stop_with_missing_pid_file(tmp_path):
    (tmp_path / "logs").mkdir()
    state = {"runtime_dir": str(tmp_path)}
    with (
        patch("nrobo.cli.commands.nginx.load_state", return_value=state),
        patch("nrobo.cli.commands.nginx.clear_state") as mock_clear,
    ):
        cmd_stop(None)
        mock_clear.assert_called_once()


def test_cmd_stop_with_no_state():
    with patch("nrobo.cli.commands.nginx.load_state", return_value=None):
        cmd_stop(None)


def test__pid_running_true():
    fake_proc = MagicMock()
    fake_proc.is_running.return_value = True
    fake_proc.name.return_value = "nginx"

    with patch("psutil.Process", return_value=fake_proc):
        assert _pid_running(1234) is True


def test__pid_running_false_on_exception():
    with patch("psutil.Process", side_effect=Exception("Boom")):
        assert _pid_running(1234) is False


class DummyState:
    def __init__(self, runtime_dir, url="http://dummy", port=1234, served_dir="/some/dir"):
        self.data = {
            "runtime_dir": str(runtime_dir),
            "url": url,
            "port": port,
            "served_dir": served_dir,
        }

    def to_dict(self):
        return self.data.copy()


# Monkeypatch for load_state / clear_state
@pytest.fixture(autouse=True)
def no_real_state(monkeypatch, tmp_path):
    # Ensure clear_state doesn't mess with real FS
    monkeypatch.setattr(nginx, "clear_state", lambda: None)
    return tmp_path


def test_status_pid_exists_but_not_running(monkeypatch, tmp_path, capsys):
    # Create dummy state with fake pid file
    runtime = tmp_path / "runtime"
    logs = runtime / "logs"
    logs.mkdir(parents=True)
    pid_file = logs / "nginx.pid"
    pid_file.write_text("999999")  # some pid that does not exist

    # monkeypatch load_state to return our dummy
    monkeypatch.setattr(
        nginx,
        "load_state",
        lambda: {
            "runtime_dir": str(runtime),
            "url": "http://localhost",
            "port": 8080,
            "served_dir": "/some/dir",
        },
    )

    # Also monkeypatch _pid_running to return False
    monkeypatch.setattr(nginx, "_pid_running", lambda pid: False)

    # Call status
    with redirect_stdout(StringIO()) as buf:
        nginx.cmd_status(argparse.Namespace())  # args not used

    out = buf.getvalue()
    assert "Alive:       No ❌" in out
    assert "Nginx PID exists but not active or listening." in out


def test_stop_no_pid_file(monkeypatch, tmp_path, capsys):
    runtime = tmp_path / "runtime"
    (runtime / "logs").mkdir(parents=True)
    # do not create pid file

    monkeypatch.setattr(
        nginx,
        "load_state",
        lambda: {
            "runtime_dir": str(runtime),
        },
    )

    with redirect_stdout(StringIO()) as buf:
        nginx.cmd_stop(argparse.Namespace())

    out = buf.getvalue()
    assert "PID file missing — cleaning stale state." in out


def test_stop_pid_exists_but_process_missing(monkeypatch, tmp_path, capsys):
    runtime = tmp_path / "runtime"
    logs = runtime / "logs"
    logs.mkdir(parents=True)
    pid_file = logs / "nginx.pid"
    pid_file.write_text("12345")

    monkeypatch.setattr(
        nginx,
        "load_state",
        lambda: {
            "runtime_dir": str(runtime),
        },
    )

    # monkeypatch os.kill to raise ProcessLookupError
    monkeypatch.setattr(os, "kill", lambda pid, sig: (_ for _ in ()).throw(ProcessLookupError()))

    with redirect_stdout(StringIO()) as buf:
        nginx.cmd_stop(argparse.Namespace())

    out = buf.getvalue()
    assert "Process not found — removing stale state." in out


def test_run_no_args_prints_help(monkeypatch, capsys):
    # If no sub‑command (empty list or None), run() should just print help and return
    # We capture stdout
    with pytest.raises(SystemExit):
        nginx.run(argv=[])  # no command
    out = capsys.readouterr().out
    assert "usage:" in out or "Manage" in out  # basic help printed


def test_run_exception_handling(monkeypatch, capsys):
    def boom(args):
        raise RuntimeError("Something exploded")

    monkeypatch.setattr(nginx, "cmd_start", boom)

    monkeypatch.setattr(nginx, "reuse_or_launch_allure_nginx", lambda x: {"url": "fake"})

    # Inject parser hook for the subcommand
    def patched_parser(*args, **kwargs):
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="command")
        start_cmd = sub.add_parser("start")
        start_cmd.add_argument("--dir")
        start_cmd.set_defaults(func=boom)
        return parser

    monkeypatch.setattr(nginx, "argparse", argparse)

    with monkeypatch.context() as m:
        m.setattr(sys, "argv", ["nginx.py", "start", "--dir", "some_dir"])
        nginx.run(["start", "--dir", "some_dir"])

    out = capsys.readouterr().out
    assert "nginx server could not be started due to error: Something exploded" in out


def test_stop_pid_exists_but_kill_fails(monkeypatch, tmp_path):
    runtime = tmp_path / "runtime"
    logs = runtime / "logs"
    logs.mkdir(parents=True)
    pid_file = logs / "nginx.pid"
    pid_file.write_text("99999")

    monkeypatch.setattr(nginx, "load_state", lambda: {"runtime_dir": str(runtime)})

    def fake_kill(pid, signal):
        raise PermissionError("not allowed")

    monkeypatch.setattr(os, "kill", fake_kill)

    with redirect_stdout(StringIO()) as buf:
        nginx.cmd_stop(argparse.Namespace())

    out = buf.getvalue()
    assert "❌ Failed to stop nginx: not allowed" in out

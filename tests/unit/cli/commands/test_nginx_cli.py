from pathlib import Path

import pytest
from unittest.mock import patch, MagicMock

from nrobo.cli.commands.nginx import cmd_start, cmd_status, cmd_stop, _pid_running


@pytest.fixture
def fake_args():
    class Args:
        dir = "/tmp/fake-allure"
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
    with patch("nrobo.cli.commands.nginx.run") as mock_run, \
         patch("sys.exit") as mock_exit:
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
        "served_dir": "/tmp",
        "runtime_dir": str(tmp_path),
    }

    with patch("nrobo.cli.commands.nginx.load_state", return_value=state), \
         patch("nrobo.cli.commands.nginx._pid_running", return_value=True):
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

    with patch("nrobo.cli.commands.nginx.load_state", return_value=state), \
         patch("nrobo.cli.commands.nginx.clear_state") as mock_clear, \
         patch("os.kill") as mock_kill:
        cmd_stop(None)
        mock_kill.assert_called_once_with(1234, 15)
        mock_clear.assert_called_once()


def test_cmd_stop_with_missing_pid_file(tmp_path):
    (tmp_path / "logs").mkdir()
    state = {"runtime_dir": str(tmp_path)}
    with patch("nrobo.cli.commands.nginx.load_state", return_value=state), \
         patch("nrobo.cli.commands.nginx.clear_state") as mock_clear:
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

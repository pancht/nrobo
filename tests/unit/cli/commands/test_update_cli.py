from unittest import mock
from unittest.mock import MagicMock

from nrobo.cli.commands import update
from nrobo.cli.commands.update import run


# --- Test --playwright flag ---
def test_run_playwright(monkeypatch, capsys):
    mp_update = MagicMock()
    mp_install = MagicMock()

    monkeypatch.setattr(update, "update_playwright_dependencies", mp_update)
    monkeypatch.setattr(update, "install_playwright_browsers", mp_install)

    update.run(["--playwright"])

    out = capsys.readouterr().out
    assert "🔄 Updating Playwright stack..." in out
    mp_update.assert_called_once()
    mp_install.assert_called_once()


# --- Test --selenium flag ---
def test_run_selenium(monkeypatch, capsys):
    mp_update = MagicMock()
    monkeypatch.setattr(update, "update_selenium_dependencies", mp_update)

    update.run(["--selenium"])

    out = capsys.readouterr().out
    assert "🔄 Updating Selenium stack..." in out
    mp_update.assert_called_once()


def test_update_self_success(capsys):
    with mock.patch("nrobo.cli.commands.update.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock()  # Simulate success
        run(["--self"])

    captured = capsys.readouterr()
    assert "🔄 Updating nrobo framework..." in captured.out
    assert "✅ Updated nrobo." in captured.out
    mock_run.assert_called_once_with(["pip", "install", "--upgrade", "nrobo"], check=True)


def test_update_self_failure(capsys):
    with mock.patch(
        "nrobo.cli.commands.update.subprocess.run", side_effect=Exception("some error")
    ):
        run(["--self"])

    captured = capsys.readouterr()
    assert "🔄 Updating nrobo framework..." in captured.out
    assert "❌ Failed to update nrobo: some error" in captured.out

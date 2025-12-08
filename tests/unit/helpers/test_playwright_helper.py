import json
import subprocess
from pathlib import Path
from unittest import mock

import nrobo.helpers.playwright_helper as ph


def test_is_playwright_installed_true(tmp_path, monkeypatch):
    # Correct simulation: ~/.cache/ms-playwright
    simulated_home = tmp_path
    browser_dir = simulated_home / ".cache" / "ms-playwright"
    browser_dir.mkdir(parents=True)
    (browser_dir / "browser_file").write_text("dummy")

    monkeypatch.setattr(Path, "home", lambda: simulated_home)
    assert ph.is_playwright_installed() is True


def test_is_playwright_installed_false(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path.parent)
    assert ph.is_playwright_installed() is False


def test_install_playwright_browsers_already_installed(monkeypatch, capsys):
    monkeypatch.setattr(ph, "is_playwright_installed", lambda: True)
    ph.install_playwright_browsers()
    output = capsys.readouterr().out
    assert "Playwright browsers already installed" in output


def test_install_playwright_browsers_success(monkeypatch, capsys):
    monkeypatch.setattr(ph, "is_playwright_installed", lambda: False)
    mock_run = mock.Mock()
    monkeypatch.setattr(subprocess, "run", mock_run)
    ph.install_playwright_browsers()
    output = capsys.readouterr().out
    assert "Installing Playwright browsers" in output
    mock_run.assert_called_once_with(["playwright", "install"], check=True)


def test_install_playwright_browsers_exception(monkeypatch, capsys):
    monkeypatch.setattr(ph, "is_playwright_installed", lambda: False)
    monkeypatch.setattr(subprocess, "run", mock.Mock(side_effect=Exception("fail")))
    ph.install_playwright_browsers()
    output = capsys.readouterr().out
    assert "❌ Failed to install Playwright browsers: fail" in output


def test_get_outdated_packages_success(monkeypatch):
    fake_output = json.dumps(
        [
            {"name": "playwright", "version": "1.30", "latest_version": "1.40"},
            {"name": "pytest", "version": "7.0", "latest_version": "7.2"},
        ]
    )
    mock_run = mock.Mock()
    mock_run.stdout = fake_output
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: mock_run)

    result = ph.get_outdated_packages()
    assert isinstance(result, list)
    assert result[0]["name"] == "playwright"


def test_get_outdated_packages_exception(monkeypatch, capsys):
    monkeypatch.setattr(subprocess, "run", mock.Mock(side_effect=Exception("list error")))
    result = ph.get_outdated_packages()
    assert result == []
    output = capsys.readouterr().out
    assert "❌ Failed to list outdated packages: list error" in output


def test_update_playwright_dependencies_up_to_date(monkeypatch, capsys):
    monkeypatch.setattr(ph, "get_outdated_packages", lambda: [])
    ph.update_playwright_dependencies()
    output = capsys.readouterr().out
    assert "Playwright packages are already up to date" in output


def test_update_playwright_dependencies_success(monkeypatch, capsys):
    outdated = [
        {"name": "playwright", "version": "1.30", "latest_version": "1.40"},
        {"name": "pytest-playwright", "version": "0.3", "latest_version": "0.4"},
    ]
    monkeypatch.setattr(ph, "get_outdated_packages", lambda: outdated)
    monkeypatch.setattr(subprocess, "run", mock.Mock())
    ph.update_playwright_dependencies()
    output = capsys.readouterr().out
    assert "Updating" in output
    assert "Updated successfully" in output


def test_update_playwright_dependencies_failure(monkeypatch, capsys):
    monkeypatch.setattr(
        ph,
        "get_outdated_packages",
        lambda: [{"name": "playwright", "version": "1.30", "latest_version": "1.40"}],
    )
    monkeypatch.setattr(subprocess, "run", mock.Mock(side_effect=Exception("update fail")))
    ph.update_playwright_dependencies()
    output = capsys.readouterr().out
    assert "❌ Failed to update: update fail" in output

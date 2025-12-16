from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from nrobo.plugins.nrobo_plugin import nRoboWebDriverPlugin
from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper


@pytest.fixture
def request_mock(monkeypatch):
    return SimpleNamespace(
        config=SimpleNamespace(getoption=lambda key: "selenium"), node=SimpleNamespace()
    )


def test_selenium_chrome(monkeypatch, request_mock):
    plugin = nRoboWebDriverPlugin()

    # Patch env
    monkeypatch.setenv("NROBO_BROWSER", "chrome")
    monkeypatch.setenv("NROBO_HEADLESS", "true")

    # Patch driver
    mock_driver = MagicMock()  # noqa: F841
    mock_wrapper = MagicMock(spec=SeleniumWrapper)
    monkeypatch.setattr(
        plugin, "_get_selenium_wrapper", lambda req, log, browser, headless: mock_wrapper
    )

    result = plugin._get_driver_wrapper(request_mock, logger=MagicMock())
    assert isinstance(result, SeleniumWrapper) or result is mock_wrapper


@pytest.mark.parametrize("browser", ["chrome", "firefox", "webkit"])
def test_playwright_browsers(monkeypatch, browser):
    plugin = nRoboWebDriverPlugin()

    monkeypatch.setenv("NROBO_BROWSER", browser)
    monkeypatch.setenv("NROBO_HEADLESS", "false")

    request_mock = SimpleNamespace(
        config=SimpleNamespace(getoption=lambda key: "playwright"), node=SimpleNamespace()
    )

    # Mock the Playwright objects
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_playwright.firefox.launch.return_value = mock_browser
    mock_playwright.webkit.launch.return_value = mock_browser

    monkeypatch.setattr(
        "nrobo.plugins.nrobo_plugin.sync_playwright",
        lambda: MagicMock(start=lambda: mock_playwright),
    )

    result = plugin._get_driver_wrapper(request_mock, logger=MagicMock())
    assert result is mock_page


def test_playwright_invalid_browser(monkeypatch):
    plugin = nRoboWebDriverPlugin()
    monkeypatch.setenv("NROBO_BROWSER", "opera")
    monkeypatch.setenv("NROBO_HEADLESS", "true")

    request_mock = SimpleNamespace(
        config=SimpleNamespace(getoption=lambda key: "playwright"), node=SimpleNamespace()
    )

    monkeypatch.setattr(
        "nrobo.plugins.nrobo_plugin.sync_playwright", lambda: MagicMock(start=lambda: MagicMock())
    )

    with pytest.raises(ValueError, match="Unsupported browser for Playwright"):
        plugin._get_driver_wrapper(request_mock, logger=MagicMock())


def test_invalid_engine(monkeypatch):
    plugin = nRoboWebDriverPlugin()
    monkeypatch.setenv("NROBO_BROWSER", "chrome")
    monkeypatch.setenv("NROBO_HEADLESS", "true")

    request_mock = SimpleNamespace(
        config=SimpleNamespace(getoption=lambda key: "unknown"), node=SimpleNamespace()
    )

    with pytest.raises(ValueError, match="Unknown engine type"):
        plugin._get_driver_wrapper(request_mock, logger=MagicMock())

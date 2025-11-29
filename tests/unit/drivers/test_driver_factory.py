import sys
from unittest.mock import MagicMock, patch

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from nrobo.drivers.driver_factory import get_driver

# Import your actual function here
# from your_module import get_driver


@pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
@pytest.mark.parametrize("headless", [True, False])
def test_get_driver_supported_browsers(browser, headless):
    with (
        patch(
            "webdriver_manager.chrome.ChromeDriverManager.install",
            return_value="/path/to/chromedriver",
        ),
        patch(
            "webdriver_manager.firefox.GeckoDriverManager.install",
            return_value="/path/to/geckodriver",
        ),
        patch(
            "webdriver_manager.microsoft.EdgeChromiumDriverManager.install",
            return_value="/path/to/edgedriver",
        ),
        patch("selenium.webdriver.Chrome") as mock_chrome,
        patch("selenium.webdriver.Firefox") as mock_firefox,
        patch("selenium.webdriver.Edge") as mock_edge,
    ):

        mock_chrome.return_value = mock_firefox.return_value = mock_edge.return_value = MagicMock(
            spec=WebDriver
        )

        driver = get_driver(browser, headless)
        assert isinstance(driver, WebDriver)

        if browser == "chrome":
            mock_chrome.assert_called_once()
        elif browser == "firefox":
            mock_firefox.assert_called_once()
        elif browser == "edge":
            mock_edge.assert_called_once()


@pytest.mark.skipif(
    sys.platform == "darwin", reason="Safari only raises EnvironmentError on non-macOS"
)
def test_safari_non_mac_raises_env_error():
    with pytest.raises(EnvironmentError, match="Safari is only supported on macOS."):
        get_driver("safari", headless=False)


def test_safari_headless_raises_not_implemented():
    with pytest.raises(NotImplementedError, match="Safari does not support headless mode"):
        get_driver("safari", headless=True)


def test_unsupported_browser_raises_value_error():
    with pytest.raises(ValueError, match="Unsupported browser: opera"):
        get_driver("opera")

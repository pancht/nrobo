import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.safari.webdriver import WebDriver as SafariDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def get_driver(browser_name: str, headless: bool = True) -> WebDriver:
    browser = browser_name.lower()

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")  # noqa: E501
        return webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options  # noqa: E501
        )

    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")  # noqa: E501
        return webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()), options=options  # noqa: E501
        )  # noqa: E501

    elif browser == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless=new")  # noqa: E501
        return webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install()),
            options=options,  # noqa: E501
        )  # noqa: E501

    elif browser == "safari":
        if headless:
            raise NotImplementedError("Safari does not support headless mode")
        if sys.platform != "darwin":
            raise EnvironmentError("Safari is only supported on macOS.")
        return SafariDriver()

    else:
        raise ValueError(f"Unsupported browser: {browser}")

import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from .drivers.driver_factory import get_driver
from nrobo.drivers.selenium_wrappers.nrobo_selenium_wrapper import NRoboSeleniumWrapperClass


class nRoboWebDriverPlugin:
    def __init__(self):
        self.driver_instance = None

    def pytest_addoption(self, parser):
        parser.addoption(
            "--browser",
            action="store",
            default="chrome",
            help="Browser to run tests: chrome, firefox, edge, safari"
        )
        parser.addoption(
            "--no-headless",
            action="store_true",
            default=False,
            help="Run browser in headed mode (default is headless)"
        )
        parser.addoption("--auto-driver", action="store_true", help="Auto use driver in tests")

    @pytest.fixture(scope="function", autouse=False)
    def driver(self, request):
        browser = request.config.getoption("--browser")
        headless = not request.config.getoption("--no-headless")
        self.driver_instance:WebDriver = get_driver(browser, headless=headless)
        wrapper:NRoboSeleniumWrapperClass = NRoboSeleniumWrapperClass(self.driver_instance)
        yield wrapper
        self.driver_instance.quit()

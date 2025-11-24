import pytest
from .drivers.driver_factory import get_driver


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

    @pytest.fixture(scope="function")
    def driver(self, request):
        browser = request.config.getoption("--browser")
        headless = not request.config.getoption("--no-headless")
        self.driver_instance = get_driver(browser, headless=headless)
        yield self.driver_instance
        self.driver_instance.quit()

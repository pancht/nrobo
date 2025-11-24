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

    @pytest.fixture(scope="function")
    def driver(self, request):
        browser = request.config.getoption("--browser")
        self.driver_instance = get_driver(browser)
        yield self.driver_instance
        self.driver_instance.quit()

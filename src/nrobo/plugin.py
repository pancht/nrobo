import logging
import os
import time

import pytest
from _pytest.config import Config
from _pytest.fixtures import FixtureRequest
from colorlog import ColoredFormatter
from selenium.webdriver.remote.webdriver import WebDriver

from nrobo.selenium_wrappers.nrobo_selenium_wrapper import NRoboSeleniumWrapperClass
from .drivers.driver_factory import get_driver
from .helpers._pytest import extract_test_name


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

    def _get_logger(self, request: FixtureRequest) -> logging.Logger:
        test_name = request.node.name
        log_dir = os.path.join("logs")
        os.makedirs(log_dir, exist_ok=True)

        logger = logging.getLogger(f"nrobo.{test_name}")
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:  # Avoid duplicate handlers
            # Console Handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            # color formatter
            formatter = ColoredFormatter(
                "%(log_color)s[%(levelname)s]%(reset)s %(message)s",
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white'
                }
            )
            ch.setFormatter(formatter)

            # File Handler
            fh = logging.FileHandler(os.path.join(log_dir, f"{test_name}.log"))
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ))

            logger.addHandler(ch)
            logger.addHandler(fh)
            logger.info(f"nrobo.{test_name}")

        return logger

    @pytest.fixture(scope="function")
    def logger(self, request) -> logging.Logger:
        return self._get_logger(request)

    @pytest.fixture(scope="function", autouse=False)
    def driver(self, request, logger):
        browser = request.config.getoption("--browser")
        headless = not request.config.getoption("--no-headless")
        self.driver_instance: WebDriver = get_driver(browser, headless=headless)

        # Inject logger
        wrapper: NRoboSeleniumWrapperClass = NRoboSeleniumWrapperClass(self.driver_instance, logger=logger)

        # Attach to item so that it wrapper can be accessed in pytest_runtest_makereport(item: Item, call)
        # for capturing screenshot of the failure
        request.node._driver_wrapper = wrapper

        yield wrapper

        self.driver_instance.quit()

    def pytest_runtest_setup(self, item):
        item.start_time = time.time()

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()

        if call.when == "call":
            end_time = time.time()
            duration = end_time - getattr(item, "start_time", end_time)

            test_name = extract_test_name(item)
            logger = logging.getLogger(f"nrobo.{test_name}")
            logger.info(f"Test Status: {report.outcome.upper()}")
            logger.info(f"Duration: {duration:.2f} seconds")

        # Example: Attach screenshot if Selenium driver present and failure
        # Get driver from item
        wrapper: NRoboSeleniumWrapperClass = getattr(item, "_driver_wrapper", None)
        if wrapper is not None and report.outcome == "failed":
            screenshots_dir = os.path.join("screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            screenshot_file = os.path.join(screenshots_dir, f"{test_name}.png")
            try:
                b64 = wrapper.driver.get_screenshot_as_base64()  # using Selenium WebDriver API
                extras = getattr(report, "extras", [])
                import pytest_html
                extras.append(pytest_html.extras.image(b64, mime_type="image/png", extension="png"))
                report.extras = extras# + [extras.image(screenshot_file)]
            except Exception as e:
                logging.getLogger(f"nrobo.{test_name}").warning(f"Could not save screenshot: {e}")

    def pytest_configure(self, config: Config):
        pass

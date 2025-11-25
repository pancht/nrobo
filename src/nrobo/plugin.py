import logging
import os
import time

import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from .drivers.driver_factory import get_driver
from nrobo.selenium_wrappers.nrobo_selenium_wrapper import NRoboSeleniumWrapperClass
from _pytest.fixtures import FixtureRequest
from colorlog import ColoredFormatter

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

        yield wrapper

        self.driver_instance.quit()

        def pytest_runtest_setup( item):
            item.start_time = time.time()

        def pytest_runtest_makereport(item, call):
            outcome = yield
            report = outcome.get_result()

            if call.when == "call":
                end_time = time.time()
                duration = end_time - getattr(item, "start_time", end_time)
                logger = logging.getLogger(f"nrobo.{item.name}")
                logger.info(f"Test Status: {report.outcome.upper()}")
                logger.info(f"Duration: {duration:.2f} seconds")

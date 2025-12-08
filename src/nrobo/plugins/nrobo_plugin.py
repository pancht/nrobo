import logging
import os
import sys
import time
from pathlib import Path

import allure
import pytest
from _pytest.config import Config
from _pytest.fixtures import FixtureRequest
from colorlog import ColoredFormatter
from selenium.webdriver.remote.webdriver import WebDriver

from nrobo.core import settings
from nrobo.drivers.driver_factory import get_driver
from nrobo.helpers._pytest_helper import extract_test_name
from nrobo.helpers._pytest_xdist import grab_worker_id, is_running_with_xdist
from nrobo.selenium_wrappers.nrobo_selenium_wrapper import (  # noqa: E501
    NRoboSeleniumWrapperClass,
)


class nRoboWebDriverPlugin:
    def __init__(self):
        self.driver_instance = None

    def pytest_addoption(self, parser):
        pass

    def _get_logger(self, request: FixtureRequest) -> logging.Logger:
        """
        Create a per-test, per-worker logger.
        Example: logs/gw0/test_example.log
        """
        node = request.node
        class_name = node.cls.__name__ if node.cls else None
        node_name = node.name
        test_name = f"{class_name}_{node_name}" if node.cls else node_name

        # ✅ detect xdist worker ID (gw0, gw1, etc.) — default to 'master' if local  # noqa: E501
        worker_id = grab_worker_id()

        # ✅ make directory structure logs/<worker_id>/
        log_dir = (
            os.path.join(settings.LOG_DIR, worker_id)
            if is_running_with_xdist()
            else os.path.join(settings.LOG_DIR)  # noqa: E501
        )
        os.makedirs(log_dir, exist_ok=True)

        unique_logger_name = (
            f"{settings.NROBO_APP}_{worker_id}_{test_name}.log"
            if is_running_with_xdist()
            else f"{settings.NROBO_APP}_{test_name}.log"
        )
        log_path = os.path.join(log_dir, unique_logger_name)

        # Initialize logger
        logger = logging.getLogger(f"{settings.NROBO_APP}_{test_name}")
        logger.setLevel(logging.DEBUG)

        # Avoid duplicate handlers (important in pytest runs)
        if logger.handlers:
            return logger  # pragma: no cover

        # Stream handler (stdout)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(settings.LOG_LEVEL_STREAM)
        ch.setFormatter(
            ColoredFormatter(
                settings.LOG_FORMAT_STREAM,
                log_colors=settings.LOG_COLORS_STREAM,
            )
        )

        # File handler (persistent logs)
        fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        fh.setLevel(settings.LOG_LEVEL_FILE)
        fh.setFormatter(logging.Formatter(settings.LOG_FORMAT_FILE))

        # Add handlers
        logger.addHandler(ch)
        logger.addHandler(fh)

        # logger.propagate = False
        if is_running_with_xdist():
            logger.info(
                f"Logger initialized for test: {test_name} (worker: {worker_id})"  # noqa: E501
            )  # noqa: E501
        else:
            logger.info(f"Logger initialized for test: {test_name}")  # pragma: no cover
        return logger

    @pytest.fixture(scope="function")
    def logger(self, request) -> logging.Logger:
        return self._get_logger(request)

    @pytest.fixture(scope="function")
    def nrobo(self, request, logger):
        env_browser = os.getenv("NROBO_BROWSER").lower()
        env_headless = os.getenv("NROBO_HEADLESS").lower().strip() == "true"
        self.driver_instance: WebDriver = get_driver(
            env_browser, headless=env_headless
        )  # noqa: E501

        # Inject logger
        nrobo_wrapper_: NRoboSeleniumWrapperClass = NRoboSeleniumWrapperClass(
            self.driver_instance, logger=logger
        )

        # Attach to item so that it wrapper can be accessed in pytest_runtest_makereport(item: Item, call) # noqa: E501
        # for capturing screenshot of the failure
        request.node._driver_wrapper = nrobo_wrapper_

        yield nrobo_wrapper_

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
            final_test_name = (
                f"{settings.NROBO_APP}_{grab_worker_id()}_{test_name}"
                if is_running_with_xdist()
                else f"{settings.NROBO_APP}_{test_name}"
            )
            logger = logging.getLogger(final_test_name)
            logger.info(f"Test Status: {report.outcome.upper()}")
            logger.info(f"Duration: {duration:.2f} seconds")

        wrapper: NRoboSeleniumWrapperClass = getattr(item, "_driver_wrapper", None)  # noqa: E501
        if wrapper is not None and report.outcome == "failed":
            screenshots_dir = Path(settings.TEST_ARTIFACTS_DIR) / settings.SCREENSHOTS
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            try:
                screenshot_file = os.path.join(  # noqa: F841
                    screenshots_dir, f"{final_test_name}.png"
                )
            except UnboundLocalError:  # noqa: E841, E501
                final_test_name = test_name = "unbounded_local_filename"
                screenshot_file = os.path.join(  # noqa: F841
                    screenshots_dir, f"{final_test_name}.png"
                )

            try:
                screenshot_bytes = wrapper.driver.get_screenshot_as_base64()
                screenshot_as_png = wrapper.driver.get_screenshot_as_png()

                # allure report handling
                allure.attach(
                    screenshot_as_png,
                    name=f"screenshot_{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )

                # using Selenium WebDriver API
                extras = getattr(report, "extras", [])
                import pytest_html

                extras.append(
                    pytest_html.extras.image(
                        screenshot_bytes, mime_type="image/png", extension="png"  # noqa: E501
                    )
                )
                report.extras = extras  # + [extras.image(screenshot_file)]
            except Exception as e:
                logging.getLogger(f"{settings.NROBO_APP}.{test_name}").warning(
                    f"Could not save screenshot: {e}"
                )  # noqa: E501
            except KeyError:  # pragma: no cover
                pass  # pragma: no cover

    def pytest_configure(self, config: Config):
        pass


def pytest_configure(config):
    """
    Called automatically by pytest in every process (master + workers).
    We register an instance of nRoboWebDriverPlugin so its fixtures
    and hooks become globally available.
    """

    # Register plugin
    plugin_instance = nRoboWebDriverPlugin()
    config.pluginmanager.register(plugin_instance, name="nrobo_webdriver_plugin")  # noqa: E501

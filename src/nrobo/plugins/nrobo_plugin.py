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
from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper


class nRoboWebDriverPlugin:
    def __init__(self):
        self.driver_instance = None
        # logging.debug("[nRoboPlugin] Plugin initialized.")

    def pytest_addoption(self, parser):
        # logging.debug("[nRoboPlugin] pytest_addoption called (no custom args).")
        pass

    # ---------------------------------------------------------------
    # Logger Setup
    # ---------------------------------------------------------------
    def _get_logger(self, request: FixtureRequest) -> logging.Logger:
        """
        Creates a per-test logger that emits **exactly one log per event**.
        Prevents duplication across stdout/stderr/pytest log capture.
        Fully xdist-safe and pytest-safe.
        """

        # ---------------------------- 1. Build test name --------------------------------
        node = request.node
        class_name = node.cls.__name__ if node.cls else None
        node_name = node.name
        test_name = f"{class_name}_{node_name}" if node.cls else node_name

        worker_id = grab_worker_id()

        # ---------------------------- 2. Log directory ----------------------------------
        log_dir = (
            os.path.join(settings.LOG_DIR, worker_id)
            if is_running_with_xdist()
            else settings.LOG_DIR
        )
        os.makedirs(log_dir, exist_ok=True)

        # ---------------------------- 3. Unique filename --------------------------------
        log_filename = (
            f"{settings.NROBO_APP}_{worker_id}_{test_name}.log"
            if is_running_with_xdist()
            else f"{settings.NROBO_APP}_{test_name}.log"
        )
        log_path = os.path.join(log_dir, log_filename)

        # ---------------------------- 4. Create logger -----------------------------------
        logger_name = f"{settings.NROBO_APP}.{test_name}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        # If already initialized (handlers exist) → reuse
        if logger.handlers:
            return logger  # pragma: no cover

        # ---------------------------- 5. STREAM HANDLER (stderr only!) --------------------
        # Do NOT use stdout → pytest duplicates stdout
        stream_handler = logging.StreamHandler(sys.stdout)  # defaults to stderr
        stream_handler.setLevel(settings.LOG_LEVEL_STREAM)
        stream_handler.setFormatter(
            ColoredFormatter(
                settings.LOG_FORMAT_STREAM,
                log_colors=settings.LOG_COLORS_STREAM,
            )
        )

        # ---------------------------- 6. FILE HANDLER ------------------------------------
        file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        file_handler.setLevel(settings.LOG_LEVEL_FILE)
        file_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT_FILE))

        # ---------------------------- 7. ATTACH HANDLERS ---------------------------------
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

        # ---------------------------- 8. Bootstrap log (to this logger only) --------------
        init_message = (
            f"Logger initialized for test: {test_name} (worker={worker_id})"
            if is_running_with_xdist()
            else f"Logger initialized for test: {test_name}"
        )
        logger.debug(init_message)

        # VERY IMPORTANT: prevent propagation → pytest cannot duplicate logs
        # logger.propagate = False

        return logger

    # ---------------------------------------------------------------
    # Fixtures
    # ---------------------------------------------------------------
    @pytest.fixture(scope="function")
    def logger(self, request) -> logging.Logger:
        # logging.debug("[Fixture:logger] Creating logger fixture.")
        return self._get_logger(request)

    @pytest.fixture(scope="function")
    def nrobo(self, request, logger):
        # logging.debug("[Fixture:nrobo] Starting WebDriver setup...")

        env_browser = os.getenv("NROBO_BROWSER", "chrome").lower()
        env_headless = os.getenv("NROBO_HEADLESS", "true").lower().strip() == "true"

        # logging.debug(f"[Fixture:nrobo] Browser={env_browser}, Headless={env_headless}")

        self.driver_instance: WebDriver = get_driver(env_browser, headless=env_headless)
        # logging.debug("[Fixture:nrobo] WebDriver created successfully.")

        nrobo_wrapper_: SeleniumWrapper = SeleniumWrapper(self.driver_instance, logger=logger)
        # logging.debug("[Fixture:nrobo] SeleniumWrapper initialized.")

        request.node._driver_wrapper = nrobo_wrapper_
        # logging.debug("[Fixture:nrobo] Wrapper attached to pytest node.")

        yield nrobo_wrapper_

        # logging.debug("[Fixture:nrobo] Test finished; quitting WebDriver.")
        self.driver_instance.quit()

    # ---------------------------------------------------------------
    # Hooks
    # ---------------------------------------------------------------
    def pytest_runtest_setup(self, item):
        # logging.debug(f"[Hook] Test setup started: {item.name}")
        item.start_time = time.time()

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_makereport(self, item, call):
        # logging.debug(f"[Hook] Preparing test report: {item.name}")

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
            # logging.debug(f"[Hook] Test report logged: {final_test_name}")

        # Screenshot section
        wrapper: SeleniumWrapper = getattr(item, "_driver_wrapper", None)
        if wrapper is not None and report.outcome == "failed":
            # logging.debug("[Hook] Failure detected; attempting screenshot capture.")

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

                allure.attach(
                    screenshot_as_png,
                    name=f"screenshot_{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )

                import pytest_html

                extras = getattr(report, "extras", [])
                extras.append(
                    pytest_html.extras.image(
                        screenshot_bytes, mime_type="image/png", extension="png"
                    )
                )
                report.extras = extras

                # logging.debug("[Hook] Screenshot captured & attached to reports.")

            except Exception as e:
                logging.error(f"[Hook] Could not save screenshot: {e}")
                logging.getLogger(f"{settings.NROBO_APP}.{test_name}").warning(
                    f"Could not save screenshot: {e}"
                )  # noqa: E501
            except KeyError:  # pragma: no cover
                pass  # pragma: no cover

    def pytest_configure(self, config: Config):
        # logging.debug("[Hook] pytest_configure called for plugin (worker/master).")
        pass


# ---------------------------------------------------------------
# Global registration entry point
# ---------------------------------------------------------------
def pytest_configure(config):
    # logging.debug("[nRoboPlugin] Registering nRoboWebDriverPlugin globally.")
    plugin_instance = nRoboWebDriverPlugin()
    config.pluginmanager.register(plugin_instance, name="nrobo_webdriver_plugin")
    # logging.debug("[nRoboPlugin] Plugin registered successfully.")

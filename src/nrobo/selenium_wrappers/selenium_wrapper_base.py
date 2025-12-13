from typing import Any

from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

from nrobo.core import settings
from nrobo.helpers.selenium_helper import _safe_ready_state
from nrobo.protocols.web_driver_protocol import SeleniumDriverProtocol
from nrobo.utils.driver_utils import is_mobile_session


class SeleniumWrapperBase:
    """Selenium wrapper with dynamic delegation and strong type support."""

    driver: SeleniumDriverProtocol  # <-- Crucial: IDE now knows driver type

    def __init__(self, driver: SeleniumDriverProtocol, logger):
        self.driver = driver
        self.logger = logger
        self._windows = {}

    # ------------------------------------
    # Automatic delegation to real driver
    # ------------------------------------
    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to the underlying Selenium driver."""
        return getattr(self.driver, name)

    # ------------------------------------
    # Windows property
    # ------------------------------------
    @property
    def windows(self) -> dict:
        return self._windows

    @windows.setter
    def windows(self, value: dict):
        self._windows = value

    def wait_for_page_load(self, timeout: int | None = None):
        if is_mobile_session(self.driver):
            return
        timeout = timeout or settings.PAGE_LOAD_TIMEOUT
        self.logger.debug(f"[nRobo] wait_for_page_to_be_loaded(timeout={timeout})")
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: _safe_ready_state(d) == "complete")
        except TimeoutException:
            self.logger.warning("[nRobo] Page did not reach 'complete' before timeout.")

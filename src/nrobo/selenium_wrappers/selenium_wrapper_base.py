from typing import Any

from nrobo.selenium_wrappers.selenium_webdriver_protocol import SeleniumDriverProtocol


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

import logging
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from nrobo.locators.locator import Locator
from nrobo.locators.locator_classifier import LocatorClassifier, LocatorType
from nrobo.mixins.auto_wait_mixin import AutoWaitMixin
from nrobo.mixins.window_mixin import WindowMixin
from nrobo.selenium_wrappers.base import SeleniumWrapperBase
from nrobo.selenium_wrappers.nrobo_types import AnyBy, AnyDriver
from nrobo.selenium_wrappers.selenium_webdriver_protocol import SeleniumDriverProtocol

PAGE_LOAD_TIMEOUT = 30
ELE_WAIT_TIMEOUT = 10


class SeleniumWrapper(SeleniumWrapperBase, AutoWaitMixin, WindowMixin):
    driver: SeleniumDriverProtocol  # helps autocompletion

    def __init__(self, driver: AnyDriver, logger: logging.Logger):
        super().__init__(driver, logger)

    def resolve_locator(self, locator: str):
        loc_type = LocatorClassifier.detect(locator)

        if loc_type == LocatorType.XPATH:
            return By.XPATH, locator

        if loc_type == LocatorType.CSS:
            return By.CSS_SELECTOR, locator

        if loc_type == LocatorType.ID:
            return By.ID, locator

        if loc_type == LocatorType.NAME:
            return By.NAME, locator

        if loc_type == LocatorType.PLAYWRIGHT:
            # Future: convert Playwright-style to Selenium (string parsing)
            raise NotImplementedError("Playwright-style locators not supported in Selenium yet.")

        return By.CSS_SELECTOR, locator  # fallback behavior

    def locator(self, locator_string: str) -> Locator:
        return Locator(self, locator_string)

    def wait_for_element_to_be_present(
        self, by: AnyBy, value: Optional[str] = None, wait: int = 0
    ) -> bool:  # noqa: E501
        """Wait for element to be visible"""

        timeout = wait or PAGE_LOAD_TIMEOUT

        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
            return True
        except Exception:  # pylint: disable=W0718
            return False

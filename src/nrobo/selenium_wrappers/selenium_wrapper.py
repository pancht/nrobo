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


class SeleniumWrapper(SeleniumWrapperBase, WindowMixin, AutoWaitMixin):
    """Final Selenium wrapper:
    - driver delegation via SeleniumWrapperBase.__getattr__
    - window helpers from WindowMixin
    - auto-wait/stale/scroll from AutoWaitMixin
    - locator factory + element actions
    """

    driver: SeleniumDriverProtocol  # enables IDE autocompletion

    def __init__(self, driver: AnyDriver, logger: logging.Logger):
        super().__init__(driver, logger)

    # -------------------------------------------------------------------------
    # Locator resolution (string → (By, value))
    # -------------------------------------------------------------------------
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
            # TODO: convert Playwright selectors to Selenium
            raise NotImplementedError("Playwright-style locators not supported yet.")

        # Fallback: treat as CSS
        return By.CSS_SELECTOR, locator

    # -------------------------------------------------------------------------
    # Public API: factory
    # -------------------------------------------------------------------------
    def locator(self, locator_string: str, description: str | None = None) -> Locator:
        return Locator(self, locator_string, description)

    # -------------------------------------------------------------------------
    # Element ACTIONS (called by Locator; AutoWaitMixin used inside)
    # -------------------------------------------------------------------------
    def click(self, locator: Locator) -> None:
        self._resolve(locator).click()

    def clear(self, locator: Locator) -> None:
        self._resolve(locator).clear()

    def send_keys(self, locator: Locator, *value) -> None:
        self._resolve(locator).send_keys(*value)

    def submit(self, locator: Locator) -> None:
        self._resolve(locator).submit()

    # -------------------------------------------------------------------------
    # Element QUERIES / PROPERTIES
    # -------------------------------------------------------------------------
    def is_displayed(self, locator: Locator) -> bool:
        return self._resolve(locator).is_displayed()

    def get_text(self, locator: Locator) -> str:
        return self._resolve(locator).text

    def get_tag_name(self, locator: Locator) -> str:
        return self._resolve(locator).tag_name

    def get_attribute(self, locator: Locator, name: str):
        return self._resolve(locator).get_attribute(name)

    def get_property(self, locator: Locator, name: str):
        return self._resolve(locator).get_property(name)

    def get_dom_attribute(self, locator: Locator, name: str):
        return self._resolve(locator).get_dom_attribute(name)

    def get_dom_property(self, locator: Locator, name: str):
        return self._resolve(locator).get_dom_property(name)

    def value_of_css_property(self, locator: Locator, prop: str) -> str:
        return self._resolve(locator).value_of_css_property(prop)

    def get_location(self, locator: Locator) -> dict:
        return self._resolve(locator).location

    def get_location_scrolled(self, locator: Locator) -> dict:
        return self._resolve(locator).location_once_scrolled_into_view

    def get_size(self, locator: Locator) -> dict:
        return self._resolve(locator).size

    def get_rect(self, locator: Locator) -> dict:
        return self._resolve(locator).rect

    def screenshot(self, locator: Locator, filename: str) -> bool:
        return self._resolve(locator).screenshot(filename)

    def screenshot_as_png(self, locator: Locator) -> bytes:
        return self._resolve(locator).screenshot_as_png()

    def screenshot_as_base64(self, locator: Locator) -> str:
        return self._resolve(locator).screenshot_as_base64()

    # -------------------------------------------------------------------------
    # Existing utility (kept from your earlier code)
    # -------------------------------------------------------------------------
    def wait_for_element_to_be_present(
        self, by: AnyBy, value: Optional[str] = None, wait: int = 0
    ) -> bool:
        timeout = wait or PAGE_LOAD_TIMEOUT
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
            return True
        except Exception:
            return False

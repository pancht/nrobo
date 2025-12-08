import logging
from typing import Optional

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from nrobo.mixins.window_mixin import WindowMixin
from nrobo.selenium_wrappers.base import SeleniumWrapperBase
from nrobo.selenium_wrappers.nrobo_types import AnyBy, AnyDriver
from nrobo.selenium_wrappers.selenium_webdriver_protocol import SeleniumDriverProtocol

PAGE_LOAD_TIMEOUT = 30
ELE_WAIT_TIMEOUT = 10


class SeleniumWrapper(SeleniumWrapperBase, WindowMixin):
    driver: SeleniumDriverProtocol  # helps autocompletion

    def __init__(self, driver: AnyDriver, logger: logging.Logger):
        super().__init__(driver, logger)

    def wait_for_element_to_be_present(
        self, by: AnyBy, value: Optional[str] = None, wait: int = 0
    ):  # noqa: E501
        """Wait for element to be visible"""

        if wait:
            try:
                WebDriverWait(self.driver, wait).until(
                    expected_conditions.presence_of_element_located([by, value])  # noqa: E501
                )
                return True
            except Exception:  # pylint: disable=W0718  # noqa: W0718
                return False

        try:
            WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT).until(
                expected_conditions.presence_of_element_located([by, value])
            )
            return True
        except Exception:  # pylint: disable=W0718
            return False

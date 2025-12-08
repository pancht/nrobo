import logging
from typing import Optional

from selenium.webdriver.support import expected_conditions as EC
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
    ) -> bool:  # noqa: E501
        """Wait for element to be visible"""

        timeout = wait or PAGE_LOAD_TIMEOUT

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))  # MUST BE TUPLE
            )
            return True
        except Exception:  # pylint: disable=W0718
            return False

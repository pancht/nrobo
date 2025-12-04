import logging
import time
from abc import ABC
from typing import Optional

from selenium.common import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from nrobo.selenium_wrappers.base import ELE_WAIT_TIMEOUT, PAGE_LOAD_TIMEOUT
from nrobo.selenium_wrappers.element import WebElementWrapper
from nrobo.selenium_wrappers.nrobo_types import AnyBy, AnyDriver
from nrobo.utils.driver_utils import is_mobile_session


class WaitsClassWrapper(WebElementWrapper, ABC):
    """
    Nrobo implementation of wait methods
    """

    def __init__(
        self, driver: AnyDriver, logger: logging.Logger
    ):  # pylint: disable=W0246; noqa: E501
        """
        Constructor - NroboSeleniumWrapper

        :param driver: reference to selenium webdriver
        :param logger: reference to logger instance
        """
        super().__init__(driver, logger)

    def wait_for_page_to_be_loaded(self):
        """Waits for give timeout time for page to completely load.
        timeout time is configurable in nrobo-config.yaml"""

        if is_mobile_session(self.driver):
            return

        # nprint("Wait for page load...", style=STYLE.HLOrange)
        try:
            # Webdriver implementation of page load timeout
            self.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

            # Custom page load timeout
            WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException as te:
            self.logger.info(f"Exception: {te}")
        except AttributeError as ae:
            self.logger.info(f"Exception: {ae}")
        # nprint("End of Wait for page load...", style=STYLE.PURPLE4)

    @staticmethod
    def wait(time_in_sec=None):
        """
        Pause for <time_in_sec>

        :param time_in_sec:
        :return:
        """
        WaitsClassWrapper.wait_for_a_while(time_in_sec)

    @staticmethod
    def wait_for_a_while(time_in_sec=None):
        """
        Pause for <time_in_sec>

        :param time_in_sec:
        :return:
        """
        if time_in_sec is None:
            time.sleep(PAGE_LOAD_TIMEOUT)
        else:
            time.sleep(PAGE_LOAD_TIMEOUT)

    def wait_for_element_to_be_invisible(self, locator: WebElement):
        """wait till <element> disappears from the UI"""

        self.logger.info("wait for element invisible")

        # wait a little
        self.wait_for_a_while(PAGE_LOAD_TIMEOUT)

        # wait until the locator becomes invisible
        try:
            WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT).until(
                expected_conditions.invisibility_of_element_located(locator)
            )
        except Exception:  # pylint: disable=W0718
            return False

        self.wait_for_a_while(PAGE_LOAD_TIMEOUT)

        self.logger.info("end of wait for element invisible")
        return True

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

    def wait_for_element_to_be_disappeared(
        self, by: AnyBy, value: Optional[str] = None, wait: int = 0
    ):
        """wait till <element> disappears from the UI"""

        # wait a little
        self.wait_for_a_while(PAGE_LOAD_TIMEOUT)

        # wait until the locator becomes invisible
        if wait:
            try:
                WebDriverWait(self.driver, wait).until(
                    expected_conditions.invisibility_of_element_located([by, value])  # noqa: E501
                )
            except Exception:  # pylint: disable=W0718
                return False

            self.wait_for_a_while(PAGE_LOAD_TIMEOUT)
            return True

        try:
            WebDriverWait(self.driver, ELE_WAIT_TIMEOUT).until(
                expected_conditions.invisibility_of_element_located([by, value])  # noqa: E501
            )
        except Exception:  # pylint: disable=W0718
            return False

        self.wait_for_a_while(PAGE_LOAD_TIMEOUT)
        return True

    def wait_for_element_to_be_clickable(
        self, by: AnyBy = None, value: Optional[str] = None
    ):  # noqa: E501
        """
        wait till element is visible and clickable.

        :param value:
        :param by:
        :param timeout:
        :return:
        """
        self.element_to_be_clickable(by, value)

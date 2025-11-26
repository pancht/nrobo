import logging
from typing import Dict, Optional, Union

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import (
    WebDriver as AppiumWebDriver,  # pylint: disable=C0412
)
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.wheel_input import WheelInput
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select

from nrobo.selenium_wrappers.desired_cap import DesiredCapabilitiesWrapper

AnyDevice = Union[PointerInput, KeyInput, WheelInput]
AnyBy = Union[By, AppiumBy]
AnyDriver = Union[None, WebDriver, AppiumWebDriver]


class SeleniumSelectWrapper(DesiredCapabilitiesWrapper):  # pylint: disable=R0901 # noqa: E501
    """Select nrobo."""

    def __init__(
        self,
        driver: AnyDriver,
        logger: logging.Logger,
        duration: int = 250,
        devices: list[AnyDevice] | None = None,
    ):
        """
        Constructor

        :param driver: reference to selenium webdriver
        :param logger: reference to logger instance
        """
        super().__init__(driver, logger, duration=duration, devices=devices)

    def select(self, by: AnyBy, value: Optional[str] = None) -> Select:
        """
        Get SELECT element

        :param by:
        :param value:
        :return:
        """
        return Select(self.find_element(by, value))

    def get_status(self) -> Dict:
        """
        Get the Appium server status

        Usage:
            driver.get_status()
        Returns:
            Dict: The status information

        """
        return self.driver.get_status()

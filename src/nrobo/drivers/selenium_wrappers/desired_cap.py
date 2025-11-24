import logging
from typing import Union

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import (  # pylint: disable=C0412
    WebDriver as AppiumWebDriver,
)  # pylint: disable=C0412
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.wheel_input import WheelInput
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from nrobo.drivers.selenium_wrappers.by import ByWrapper

AnyDevice = Union[PointerInput, KeyInput, WheelInput]
AnyBy = Union[By, AppiumBy]
AnyDriver = Union[None, WebDriver, AppiumWebDriver]

class DesiredCapabilitiesWrapper(ByWrapper):  # pylint: disable=R0901
    """Wrapper class for selenium class: DesiredCapabilities"""

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


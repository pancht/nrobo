import logging
import typing

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import (
    WebDriver as AppiumWebDriver,  # pylint: disable=C0412
)
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.wheel_input import WheelInput
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from nrobo.selenium_wrappers.alerts import AlertWrapper

AnyDevice = typing.Union[PointerInput, KeyInput, WheelInput]
AnyBy = typing.Union[By, AppiumBy]
AnyDriver = typing.Union[None, WebDriver, AppiumWebDriver]


class ByWrapper(AlertWrapper):
    """
    Wrapper class for selenium class: By
    """

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

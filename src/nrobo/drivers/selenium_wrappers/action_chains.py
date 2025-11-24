

import logging
import typing

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import (  # pylint: disable=C0412
    WebDriver as AppiumWebDriver,
)  # pylint: disable=C0412
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.wheel_input import WheelInput
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from nrobo.drivers.selenium_wrappers.base import SeleniumWrapperBase

AnyDevice = typing.Union[PointerInput, KeyInput, WheelInput]
AnyBy = typing.Union[By, AppiumBy]
AnyDriver = typing.Union[None, WebDriver, AppiumWebDriver]


class ActionChainsWrapper(SeleniumWrapperBase):
    """Action chains nrobo."""

    def __init__(
        self,
        driver: AnyDriver,
        logger: logging.Logger,
        duration: int = 250,
        devices: list[AnyDevice] | None = None,
    ):
        """
        Constructor - NroboSeleniumWrapper

        :param driver: reference to selenium webdriver
        :param logger: reference to logger instance
        """
        super().__init__(driver, logger)
        self._action_chain = ActionChains(
            self.driver, duration=duration, devices=devices
        )

    def action_chain(self):
        """Return ActionChains object"""
        return self._action_chain
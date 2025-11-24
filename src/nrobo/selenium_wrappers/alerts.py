import logging
import typing

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import (  # pylint: disable=C0412
    WebDriver as AppiumWebDriver,
)  # pylint: disable=C0412
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.wheel_input import WheelInput
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from nrobo.selenium_wrappers.waits import WaitsClassWrapper

AnyDevice = typing.Union[PointerInput, KeyInput, WheelInput]
AnyBy = typing.Union[By, AppiumBy]
AnyDriver = typing.Union[None, WebDriver, AppiumWebDriver]

class AlertWrapper(WaitsClassWrapper):
    """Alert nrobo."""

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
        self.devices = devices
        self.duration = duration

    def accept_alert(self) -> None:
        """accept alert"""
        self.driver.switch_to.alert.accept()

    def dismiss_alert(self) -> None:
        """dismiss alert"""
        self.driver.switch_to.alert.dismiss()

    # def send_keys_to_alert(self, keysToSend: str) -> None:
    #     """Send Keys to the Alert.
    #
    #     :Args:
    #      - keysToSend: The text to be sent to Alert.
    #     """
    #     self.driver.switch_to.alert.send_keys(keysToSend)

    def send_keys_and_accept_alert(self, keys_to_send: str) -> None:
        """Send Keys to the Alert and accept it.

        :Args:
         - keysToSend: The text to be sent to Alert.
        """
        self.driver.switch_to.alert.send_keys(keys_to_send)
        self.driver.switch_to.alert.accept()

    def get_alert_text(self) -> str:
        """Get alert text"""
        return self.driver.switch_to.alert.text
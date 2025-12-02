import logging
from abc import ABC

from nrobo.selenium_wrappers.nrobo_types import AnyDevice, AnyDriver
from nrobo.selenium_wrappers.waits import WaitsClassWrapper


class AlertWrapper(WaitsClassWrapper, ABC):
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

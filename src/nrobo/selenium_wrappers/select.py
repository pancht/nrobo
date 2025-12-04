import logging
from abc import ABC
from typing import Dict, Optional

from selenium.webdriver.support.select import Select

from nrobo.selenium_wrappers.desired_cap import DesiredCapabilitiesWrapper
from nrobo.selenium_wrappers.nrobo_types import AnyBy, AnyDevice, AnyDriver


class SeleniumSelectWrapper(DesiredCapabilitiesWrapper, ABC):  # pylint: disable=R0901 # noqa: E501
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

import logging
from abc import ABC

from selenium.webdriver import ActionChains

from nrobo.selenium_wrappers.base import SeleniumWrapperBase
from nrobo.selenium_wrappers.nrobo_types import AnyDevice, AnyDriver


class ActionChainsWrapper(SeleniumWrapperBase, ABC):
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
        )  # noqa: E501

    def action_chain(self):
        """Return ActionChains object"""
        return self._action_chain

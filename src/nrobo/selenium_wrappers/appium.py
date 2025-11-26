import logging
from abc import ABC

from nrobo.nrobo_types import AnyDevice, AnyDriver
from nrobo.selenium_wrappers.select import SeleniumSelectWrapper


class NRoboAppiumWrapper(SeleniumSelectWrapper, ABC):  # pylint: disable=R0901
    """Appium specific nRoBo methods"""

    def __init__(
        self,
        driver: AnyDriver,
        logger: logging.Logger,
        duration: int = 250,
        devices: list[AnyDevice] | None = None,
    ):
        """constructor"""
        super().__init__(driver, logger, duration=duration, devices=devices)

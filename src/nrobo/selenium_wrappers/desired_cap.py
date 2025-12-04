import logging
from abc import ABC

from nrobo.selenium_wrappers.by import ByWrapper
from nrobo.selenium_wrappers.nrobo_types import AnyDevice, AnyDriver


class DesiredCapabilitiesWrapper(ByWrapper, ABC):  # pylint: disable=R0901
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

import logging
from abc import ABC

from nrobo.selenium_wrappers.alerts import AlertWrapper
from nrobo.selenium_wrappers.nrobo_types import AnyDevice, AnyDriver


class ByWrapper(AlertWrapper, ABC):
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

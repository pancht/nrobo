import logging

from nrobo.nrobo_types import AnyDevice, AnyDriver
from nrobo.selenium_wrappers.nrobo_selenium_wrapper import (  # noqa: E501
    NRoboSeleniumWrapperClass,
)


class PageHome(NRoboSeleniumWrapperClass):  # pylint: disable=R0901
    def __init__(
        self,
        driver: AnyDriver,
        logger: logging.Logger,
        duration: int = 250,
        devices: list[AnyDevice] | None = None,
    ):
        """constructor"""
        # call parent constructor
        super().__init__(driver, logger, duration=duration, devices=devices)

    ##################################################
    # Implement application specific _page methods here
    ##################################################

from nrobo.nrobo_types import AnyDevice
from nrobo.selenium_wrappers.nrobo_selenium_wrapper import (  # noqa: E501
    NRoboSeleniumWrapperClass,
)


class PageHome(NRoboSeleniumWrapperClass):  # pylint: disable=R0901
    def __init__(
        self,
        nrobo_wrapper: NRoboSeleniumWrapperClass,
        duration: int = 250,
        devices: list[AnyDevice] | None = None,
    ):
        """constructor"""
        # call parent constructor
        self.nrobo_wrapper = nrobo_wrapper
        super().__init__(
            nrobo_wrapper.driver,
            nrobo_wrapper.logger,
            duration=duration,
            devices=devices,  # noqa: E501
        )

    ##################################################
    # Implement application specific _page methods here
    ##################################################

# nrobo_wrapper.py


import logging

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.common.window import WindowTypes

from nrobo.selenium_wrappers.nrobo_custom import NRoBoCustomMethods
from nrobo.selenium_wrappers.nrobo_types import AnyDevice, AnyDriver


class NRoboSeleniumWrapperClass(NRoBoCustomMethods):
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
        super().__init__(driver, logger, duration=duration, devices=devices)

        # objects from common classes
        self.keys = Keys()
        self.by = By()
        self.print_options = PrintOptions()
        self.window_types = WindowTypes()
        self.scrolled_height = 0

        # wait for page load
        self.wait_for_page_to_be_loaded()

    def scroll_down(self):
        """scroll down web page by its scroll height"""
        screen_height = int(self.driver.execute_script("return screen.height"))
        self.driver.execute_script(
            f"window.scrollTo({self.scrolled_height}, "
            f"{self.scrolled_height + screen_height})"  # noqa: E501
        )
        self.scrolled_height += screen_height

    def scroll_to_top(self):
        """scroll to top of the page"""
        self.scrolled_height = 0
        self.driver.execute_script(
            f"window.scrollTo({self.scrolled_height}, "
            f"{self.scrolled_height})"  # noqa: E501
        )

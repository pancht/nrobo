import logging

from nrobo.mixins.window_mixin import WindowMixin
from nrobo.selenium_wrappers.base import SeleniumWrapperBase
from nrobo.selenium_wrappers.nrobo_types import AnyDriver
from nrobo.selenium_wrappers.selenium_webdriver_protocol import SeleniumDriverProtocol


class SeleniumWrapper(SeleniumWrapperBase, WindowMixin):
    driver: SeleniumDriverProtocol  # helps autocompletion

    def __init__(self, driver: AnyDriver, logger: logging.Logger):
        super().__init__(driver, logger)

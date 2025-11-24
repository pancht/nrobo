import logging
from pathlib import Path
from typing import Union, Optional

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import (  # pylint: disable=C0412
    WebDriver as AppiumWebDriver,
)  # pylint: disable=C0412
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.wheel_input import WheelInput
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from nrobo.drivers.selenium_wrappers.appium import NRoboAppiumWrapper

AnyDevice = Union[PointerInput, KeyInput, WheelInput]
AnyBy = Union[By, AppiumBy]
AnyDriver = Union[None, WebDriver, AppiumWebDriver]

class NRoBoCustomMethods(NRoboAppiumWrapper):  # pylint: disable=R0901
    """NRobo Advanced and custom methods"""

    def __init__(
        self,
        driver: AnyDriver,
        logger: logging.Logger,
        duration: int = 250,
        devices: list[AnyDevice] | None = None,
    ):
        """constructor"""
        super().__init__(driver, logger, duration=duration, devices=devices)

    def file_upload(  # pylint: disable=R0901,R0913,R0917
        self,
        file_input_by: By,
        file_input_value: str,
        file_path: Path | str,
        upload_ele_by: By,
        upload_ele_value: str,
    ):
        """
        Upload given file

        :param file_input_by: By type of file input element
        :param file_input_value: By value of file input element
        :param file_path: absolute path of file to be uploaded
        :param upload_ele_by: By type of upload action element
        :param upload_ele_value: By value of upload action element
        :return:
        """
        if isinstance(file_path, Path):
            file_path = str(file_path.absolute())

        self.find_element(file_input_by, file_input_value).send_keys(file_path)

        self.click(upload_ele_by, upload_ele_value)

    def type_into(  # pylint: disable=W1113
        self, by: AnyBy, value: Optional[str] = None, *text
    ) -> None:  # pylint: disable=W1113
        """Type given text into given element located by (by, value)"""
        self.send_keys(by, value, text)

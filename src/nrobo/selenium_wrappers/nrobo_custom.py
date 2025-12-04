import logging
from abc import ABC
from pathlib import Path
from typing import Optional

from selenium.webdriver.common.by import By

from nrobo.selenium_wrappers.appium import NRoboAppiumWrapper
from nrobo.selenium_wrappers.nrobo_types import AnyBy, AnyDevice, AnyDriver


class NRoBoCustomMethods(NRoboAppiumWrapper, ABC):  # pylint: disable=R0901
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

    def is_page_visible(self) -> bool:
        pass

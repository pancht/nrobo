from typing import Union

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import (
    WebDriver as AppiumWebDriver,  # pylint: disable=C0412
)
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.wheel_input import WheelInput
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

AnyBy = Union[By, AppiumBy]
AnyDriver = Union[None, WebDriver, AppiumWebDriver]
AnyDevice = Union[PointerInput, KeyInput, WheelInput]

from typing import Union

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.wheel_input import WheelInput
from selenium.webdriver.common.by import By

from nrobo.selenium_wrappers.selenium_webdriver_protocol import SeleniumDriverProtocol

AnyBy = Union[By, AppiumBy]
AnyDriver = SeleniumDriverProtocol  # For future where playwright protocol will be added
AnyDevice = Union[PointerInput, KeyInput, WheelInput]

from unittest.mock import MagicMock

from nrobo.utils.driver_utils import is_mobile_session


def test_mobile_session_with_android_platform():
    driver = MagicMock()
    driver.capabilities = {"platformName": "Android"}
    assert is_mobile_session(driver) is True


def test_mobile_session_with_ios_platform():
    driver = MagicMock()
    driver.capabilities = {"platformName": "iOS"}
    assert is_mobile_session(driver) is True


def test_mobile_session_with_device_name_only():
    driver = MagicMock()
    driver.capabilities = {"deviceName": "Pixel 5"}
    assert is_mobile_session(driver) is True


def test_mobile_session_with_automation_name_only():
    driver = MagicMock()
    driver.capabilities = {"automationName": "UiAutomator2"}
    assert is_mobile_session(driver) is True


def test_non_mobile_session_with_windows_platform():
    driver = MagicMock()
    driver.capabilities = {"platformName": "Windows"}
    assert is_mobile_session(driver) is False


def test_non_mobile_session_with_empty_capabilities():
    driver = MagicMock()
    driver.capabilities = {}
    assert is_mobile_session(driver) is False


def test_capabilities_attribute_missing():
    driver = MagicMock()
    del driver.capabilities  # simulate missing attribute
    assert is_mobile_session(driver) is False

from unittest.mock import MagicMock

import pytest

from nrobo.mixins.screenshot_mixin import ScreenshotMixin


class DummyScreenshotMixin(ScreenshotMixin):
    def __init__(self, driver):
        self.driver = driver


def test_save_screenshot_success():
    driver = MagicMock()
    driver.save_screenshot.return_value = True
    mixin = DummyScreenshotMixin(driver)

    result = mixin.save_screenshot("/path/image.png")

    assert result is True
    driver.save_screenshot.assert_called_once_with("/path/image.png")


def test_save_screenshot_failure():
    driver = MagicMock()
    driver.save_screenshot.return_value = False
    mixin = DummyScreenshotMixin(driver)

    result = mixin.save_screenshot("/path/bad.png")

    assert result is False
    driver.save_screenshot.assert_called_once_with("/path/bad.png")


def test_save_screenshot_raises_exception():
    driver = MagicMock()
    driver.save_screenshot.side_effect = IOError("disk error")
    mixin = DummyScreenshotMixin(driver)

    with pytest.raises(IOError):
        mixin.save_screenshot("/path/error.png")

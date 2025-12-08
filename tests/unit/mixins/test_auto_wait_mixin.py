from unittest.mock import MagicMock, patch

import pytest
from selenium.common import (
    StaleElementReferenceException,
    TimeoutException,
)

from nrobo.mixins.auto_wait_mixin import AutoWaitMixin


class DummyLocator:
    def __init__(self, by="id", value="test", description="test-locator"):
        self.by = by
        self.value = value
        self.description = description


class DummyAutoWait(AutoWaitMixin):
    def __init__(self, driver):
        self.driver = driver


@patch("nrobo.mixins.auto_wait_mixin.WebDriverWait")
def test_resolve_success(mock_wait):
    driver = MagicMock()
    mixin = DummyAutoWait(driver)

    element = MagicMock()
    # WebDriverWait.until returns our element
    mock_wait.return_value.until.return_value = element

    locator = DummyLocator()

    result = mixin._resolve(locator)

    assert result is element
    mock_wait.assert_called_once()
    driver.execute_script.assert_called_once()


@patch("nrobo.mixins.auto_wait_mixin.WebDriverWait")
def test_resolve_scroll_failure(mock_wait):
    driver = MagicMock()
    driver.execute_script.side_effect = Exception("scroll error")

    mixin = DummyAutoWait(driver)

    element = MagicMock()
    mock_wait.return_value.until.return_value = element

    result = mixin._resolve(DummyLocator())

    assert result is element
    # Script was attempted but failed
    driver.execute_script.assert_called_once()


@patch("nrobo.mixins.auto_wait_mixin.WebDriverWait")
def test_resolve_stale_then_success(mock_wait):
    driver = MagicMock()
    mixin = DummyAutoWait(driver)

    element = MagicMock()

    # First call → stale element
    # Second call → returns element
    mock_wait.return_value.until.side_effect = [
        StaleElementReferenceException("stale"),
        element,
    ]

    locator = DummyLocator()

    result = mixin._resolve(locator)

    assert result is element
    assert mock_wait.return_value.until.call_count == 2


@patch("nrobo.mixins.auto_wait_mixin.WebDriverWait")
def test_resolve_stale_exhausted(mock_wait):
    driver = MagicMock()
    mixin = DummyAutoWait(driver)

    # 3 stale attempts (RETRY_STALE_ATTEMPTS = 3)
    mock_wait.return_value.until.side_effect = [
        StaleElementReferenceException("stale1"),
        StaleElementReferenceException("stale2"),
        StaleElementReferenceException("stale3"),
    ]

    locator = DummyLocator()

    with pytest.raises(StaleElementReferenceException):
        mixin._resolve(locator)


@patch("nrobo.mixins.auto_wait_mixin.WebDriverWait")
def test_resolve_timeout(mock_wait):
    driver = MagicMock()
    mixin = DummyAutoWait(driver)

    mock_wait.return_value.until.side_effect = TimeoutException("timeout")

    with pytest.raises(TimeoutException):
        mixin._resolve(DummyLocator())


def test_perform_calls_resolve_and_action():
    driver = MagicMock()
    mixin = DummyAutoWait(driver)

    fake_el = MagicMock()
    mixin._resolve = MagicMock(return_value=fake_el)

    action = MagicMock(return_value="done")

    locator = DummyLocator()

    result = mixin._perform(locator, action)

    assert result == "done"
    mixin._resolve.assert_called_once_with(locator)
    action.assert_called_once_with(fake_el)


def test_wait_for_condition_success():
    driver = MagicMock()
    mixin = DummyAutoWait(driver)

    el = MagicMock()
    mixin._resolve = MagicMock(return_value=el)

    condition = MagicMock(return_value=True)

    locator = DummyLocator()

    result = mixin._wait_for_condition(locator, condition, timeout=1)

    assert result == locator


def test_wait_for_condition_timeout():
    driver = MagicMock()
    mixin = DummyAutoWait(driver)

    mixin._resolve = MagicMock(return_value=MagicMock())
    condition = MagicMock(return_value=False)

    with pytest.raises(AssertionError):
        mixin._wait_for_condition(DummyLocator(), condition, timeout=0.3)


def test_wait_for_condition_raises_last_exception():
    driver = MagicMock()
    mixin = DummyAutoWait(driver)

    # _resolve will fail every time
    mixin._resolve = MagicMock(side_effect=RuntimeError("boom"))

    with pytest.raises(RuntimeError):
        mixin._wait_for_condition(DummyLocator(), lambda el: True, timeout=0.3)

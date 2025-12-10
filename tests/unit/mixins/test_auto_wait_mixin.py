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
    """Concrete subclass with mocked logger and driver for testing."""

    def __init__(self):
        self.driver = MagicMock()
        self.logger = MagicMock()

    def wait_for_page_load(self):
        """Mock wait-for-load method."""
        self.logger.info("wait_for_page_load called")
        return "done"


@patch("nrobo.mixins.auto_wait_mixin.WebDriverWait")
def test_resolve_success(mock_wait):
    driver = MagicMock()
    mixin = DummyAutoWait()
    mixin.driver = driver

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

    mixin = DummyAutoWait()
    mixin.driver = driver

    element = MagicMock()
    mock_wait.return_value.until.return_value = element

    result = mixin._resolve(DummyLocator())

    assert result is element
    # Script was attempted but failed
    driver.execute_script.assert_called_once()


@patch("nrobo.mixins.auto_wait_mixin.WebDriverWait")
def test_resolve_stale_then_success(mock_wait):
    driver = MagicMock()
    mixin = DummyAutoWait()
    mixin.driver = driver

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
    mixin = DummyAutoWait()
    mixin.driver = driver

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
    mixin = DummyAutoWait()
    mixin.driver = driver

    mock_wait.return_value.until.side_effect = TimeoutException("timeout")

    with pytest.raises(TimeoutException):
        mixin._resolve(DummyLocator())


def test_perform_calls_resolve_and_action():
    driver = MagicMock()
    mixin = DummyAutoWait()
    mixin.driver = driver

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
    mixin = DummyAutoWait()
    mixin.driver = driver

    el = MagicMock()
    mixin._resolve = MagicMock(return_value=el)

    condition = MagicMock(return_value=True)

    locator = DummyLocator()

    result = mixin._wait_for_condition(locator, condition, timeout=1)

    assert result == locator


def test_wait_for_condition_timeout():
    driver = MagicMock()
    mixin = DummyAutoWait()
    mixin.driver = driver

    mixin._resolve = MagicMock(return_value=MagicMock())
    condition = MagicMock(return_value=False)

    with pytest.raises(AssertionError):
        mixin._wait_for_condition(DummyLocator(), condition, timeout=0.3)


def test_wait_for_condition_raises_last_exception():
    driver = MagicMock()
    mixin = DummyAutoWait()
    mixin.driver = driver  # patch after creation

    # _resolve will fail every time
    mixin._resolve = MagicMock(side_effect=RuntimeError("boom"))

    with pytest.raises(RuntimeError):
        mixin._wait_for_condition(DummyLocator(), lambda el: True, timeout=0.3)


def test_url_returns_current_url():
    obj = DummyAutoWait()
    obj.driver.current_url = "https://example.com"
    assert obj._url() == "https://example.com"


def test_url_handles_exception_and_returns_empty_string():
    obj = DummyAutoWait()
    type(obj.driver).current_url = property(lambda _: (_ for _ in ()).throw(Exception("fail")))
    result = obj._url()
    assert result == ""


# -------------------------------------------------------------------------
# _maybe_wait_for_nav()
# -------------------------------------------------------------------------


@patch("nrobo.mixins.auto_wait_mixin.is_mobile_session", return_value=False)
@patch("nrobo.mixins.auto_wait_mixin._safe_ready_state", return_value="complete")
def test_maybe_wait_for_nav_mode_none_and_mobile_skipped(mock_ready, mock_mobile):
    obj = DummyAutoWait()

    # Case 1: mode == "none"
    result_none = obj._maybe_wait_for_nav("url", "complete", "none")
    assert result_none is None

    # Case 2: mode == "none" but mobile session True
    mock_mobile.return_value = True
    result_mobile = obj._maybe_wait_for_nav("url", "complete", "auto")
    assert result_mobile is None


@patch("nrobo.mixins.auto_wait_mixin.is_mobile_session", return_value=False)
@patch("nrobo.mixins.auto_wait_mixin._safe_ready_state", return_value="complete")
def test_maybe_wait_for_nav_mode_load_calls_wait_for_page_load(mock_ready, mock_mobile):
    obj = DummyAutoWait()
    result = obj._maybe_wait_for_nav("url", "complete", "load")
    obj.logger.info.assert_called_with("wait_for_page_load called")
    assert result == "done"


@patch("nrobo.mixins.auto_wait_mixin.is_mobile_session", return_value=False)
def test_maybe_wait_for_nav_auto_triggers_wait_when_nav_detected(mock_mobile):
    obj = DummyAutoWait()
    obj._url = MagicMock(return_value="https://new-page.com")

    with patch("nrobo.mixins.auto_wait_mixin._safe_ready_state", return_value="loading"):
        obj._maybe_wait_for_nav("https://old.com", "complete", "auto")

    obj.logger.debug.assert_called_once()
    obj.logger.info.assert_called_with("wait_for_page_load called")


@patch("nrobo.mixins.auto_wait_mixin.is_mobile_session", return_value=False)
def test_maybe_wait_for_nav_auto_no_nav_detected_does_nothing(mock_mobile):
    obj = DummyAutoWait()
    obj._url = MagicMock(return_value="same-url")
    with patch("nrobo.mixins.auto_wait_mixin._safe_ready_state", return_value="complete"):
        obj._maybe_wait_for_nav("same-url", "complete", "auto")

    obj.logger.debug.assert_not_called()
    obj.logger.info.assert_not_called()


# -------------------------------------------------------------------------
# goto(), click(), back(), forward(), refresh()
# -------------------------------------------------------------------------


@patch.object(DummyAutoWait, "_maybe_wait_for_nav")
def test_goto_calls_driver_get_and_wait(mock_wait):
    obj = DummyAutoWait()
    obj.goto("https://example.com", wait="load")
    obj.driver.get.assert_called_once_with("https://example.com")
    mock_wait.assert_called_once()
    obj.logger.info.assert_called_with("Go to: https://example.com")


@patch("nrobo.mixins.auto_wait_mixin._safe_ready_state", return_value="complete")
@patch.object(DummyAutoWait, "_maybe_wait_for_nav")
def test_click_triggers_resolve_and_click(mock_wait, mock_ready):
    obj = DummyAutoWait()
    mock_locator = MagicMock(description="Submit button")
    fake_element = MagicMock()
    obj._resolve = MagicMock(return_value=fake_element)

    obj.click(mock_locator, wait="auto")

    fake_element.click.assert_called_once()
    obj.logger.debug.assert_called_once()
    mock_wait.assert_called_once()


@patch("nrobo.mixins.auto_wait_mixin._safe_ready_state", return_value="complete")
@patch.object(DummyAutoWait, "_maybe_wait_for_nav")
def test_back_forward_refresh_each_call_maybe_wait(mock_wait, mock_ready):
    obj = DummyAutoWait()

    for action in ("back", "forward", "refresh"):
        getattr(obj.driver, action).return_value = None
        getattr(obj, action)(wait="auto")
        getattr(obj.driver, action).assert_called_once()
        mock_wait.assert_called()

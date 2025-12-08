from unittest.mock import MagicMock, patch

from selenium.common import UnexpectedAlertPresentException

from nrobo.mixins.window_mixin import WindowMixin


class DummyWindowMixin(WindowMixin):
    """Expose WindowMixin with injectable driver + logger."""

    def __init__(self, driver):
        self.driver = driver
        self.logger = MagicMock()
        self.windows = {}


def test_update_windows_empty_list():
    mixin = DummyWindowMixin(driver=MagicMock())

    assert mixin.update_windows(None) == {}
    assert mixin.update_windows([]) == {}
    mixin.logger.warning.assert_not_called()


@patch("nrobo.mixins.window_mixin.is_mobile_session", return_value=True)
def test_update_windows_mobile_session(mock_mobile):
    driver = MagicMock()
    mixin = DummyWindowMixin(driver)

    result = mixin.update_windows(["w1", "w2"])
    assert result == {}

    # Should not query current window handle or switch_to
    driver.switch_to.window.assert_not_called()


@patch("nrobo.mixins.window_mixin.is_mobile_session", return_value=False)
def test_update_windows_current_handle_error(_):
    driver = MagicMock()
    mixin = DummyWindowMixin(driver)

    # Must mock on the driver, not the mixin
    driver.current_window_handle = MagicMock(side_effect=Exception("no handle"))

    result = mixin.update_windows(["w1", "w2"])

    assert result == {}
    mixin.logger.warning.assert_called_once()


@patch("nrobo.mixins.window_mixin.is_mobile_session", return_value=False)
def test_update_windows_normal_flow(_):
    driver = MagicMock()
    mixin = DummyWindowMixin(driver)

    # Simulate current window
    mixin.current_window_handle = "main"

    # Simulated window titles
    mixin.title = "Main Window"

    # Make switch_to_window update mixin.title dynamically
    def switch_to_side_effect(wh):
        mixin.title = f"Title-{wh}"

    mixin.switch_to_window = MagicMock(side_effect=switch_to_side_effect)

    result = mixin.update_windows(["w1", "w2"])

    # Assert mapping built correctly
    assert result == {"Title-w1": "w1", "Title-w2": "w2"}

    # Original window restored
    mixin.switch_to_window.assert_any_call("main")

    assert mixin.windows == result


@patch("nrobo.mixins.window_mixin.is_mobile_session", return_value=False)
def test_update_windows_alert_during_switch(_):
    driver = MagicMock()
    mixin = DummyWindowMixin(driver)

    mixin.current_window_handle = "main"

    def switch_side_effect(wh):
        if wh == "bad":
            raise UnexpectedAlertPresentException("alert!")
        mixin.title = f"Title-{wh}"

    mixin.switch_to_window = MagicMock(side_effect=switch_side_effect)

    result = mixin.update_windows(["good", "bad"])

    # Only good window recorded
    assert result == {"Title-good": "good"}

    # Warning logged for alert
    mixin.logger.warning.assert_called_once_with("Alert interrupted window detection.")

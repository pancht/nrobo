from unittest.mock import MagicMock

from nrobo.mixins.timeout_mixin import TimeoutMixin


class DummyTimeoutMixin(TimeoutMixin):
    def __init__(self, driver):
        self.driver = driver


def test_implicitly_wait_calls_driver():
    driver = MagicMock()
    mixin = DummyTimeoutMixin(driver)

    mixin.implicitly_wait(10)

    driver.implicitly_wait.assert_called_once_with(10)


def test_set_script_timeout_calls_driver():
    driver = MagicMock()
    mixin = DummyTimeoutMixin(driver)

    mixin.set_script_timeout(5.5)

    driver.set_script_timeout.assert_called_once_with(5.5)


def test_timeout_methods_do_not_raise():
    driver = MagicMock()
    mixin = DummyTimeoutMixin(driver)

    # no exceptions expected
    mixin.implicitly_wait(2)
    mixin.set_script_timeout(3)

    assert driver.implicitly_wait.called
    assert driver.set_script_timeout.called


def test_non_numeric_values_pass_through():
    driver = MagicMock()
    mixin = DummyTimeoutMixin(driver)

    mixin.implicitly_wait("30")  # string, allowed as-is
    mixin.set_script_timeout(None)

    driver.implicitly_wait.assert_called_once_with("30")
    driver.set_script_timeout.assert_called_once_with(None)

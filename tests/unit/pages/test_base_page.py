from types import SimpleNamespace

import pytest

from nrobo.pages.base_page import BasePage
from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper


def test_base_page_with_selenium_wrapper(mocker):
    """
    BasePage should correctly initialize when passed a SeleniumWrapper.
    """
    mock_driver = mocker.Mock(name="selenium_driver")
    mock_logger = mocker.Mock(name="logger")

    selenium_wrapper = mocker.Mock(spec=SeleniumWrapper)
    selenium_wrapper.driver = mock_driver
    selenium_wrapper.logger = mock_logger

    page = BasePage(selenium_wrapper)

    assert page.page is selenium_wrapper
    assert page.driver is mock_driver
    assert page.logger is mock_logger


def test_base_page_with_playwright_page_and_logger(mocker):
    """
    BasePage should correctly initialize when passed a Playwright Page
    and attach logger if present.
    """
    try:
        from playwright.sync_api import Page as PlaywrightPage
    except ImportError:
        pytest.skip("Playwright not installed")

    mock_page = mocker.Mock(spec=PlaywrightPage)
    mock_logger = mocker.Mock(name="logger")
    mock_page.logger = mock_logger

    page = BasePage(mock_page)

    assert page.page is mock_page
    assert page.driver is mock_page
    assert page.logger is mock_logger


def test_base_page_with_playwright_page_without_logger(mocker):
    """
    BasePage should allow Playwright Page without a logger attribute.
    """
    try:
        from playwright.sync_api import Page as PlaywrightPage
    except ImportError:
        pytest.skip("Playwright not installed")

    mock_page = mocker.Mock(spec=PlaywrightPage)
    if hasattr(mock_page, "logger"):
        delattr(mock_page, "logger")

    page = BasePage(mock_page)

    assert page.page is mock_page
    assert page.driver is mock_page
    assert page.logger is None


def test_base_page_with_unsupported_type():
    """
    BasePage should raise TypeError for unsupported page object types.
    """
    unsupported_obj = SimpleNamespace()

    with pytest.raises(TypeError, match="Unsupported page object type"):
        BasePage(unsupported_obj)


def test_base_page_playwright_not_installed(monkeypatch):
    """
    BasePage should still raise TypeError if Playwright is unavailable
    and a non-Selenium object is passed.
    """
    monkeypatch.setattr(
        "nrobo.pages.base_page.PlaywrightPage",
        None,
        raising=False,
    )

    class FakePage:
        pass

    with pytest.raises(TypeError):
        BasePage(FakePage())

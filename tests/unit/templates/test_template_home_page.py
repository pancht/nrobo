from unittest.mock import MagicMock, create_autospec

import pytest
from selenium.webdriver.common.by import By

from nrobo.selenium_wrappers.nrobo_selenium_wrapper import NRoboSeleniumWrapperClass
from nrobo.templates.home_page import PageHome


@pytest.fixture
def mock_nrobo():
    mock = create_autospec(NRoboSeleniumWrapperClass)
    mock.driver = MagicMock()
    mock.logger = MagicMock()
    return mock


def test_page_home_initialization(mock_nrobo):
    page = PageHome(wrapper=mock_nrobo)
    assert page.driver == mock_nrobo.driver
    assert page.logger == mock_nrobo.logger
    assert page.nrobo == mock_nrobo
    assert page.txta_search == (By.NAME, "q")


def test_page_home_search(mock_nrobo):
    page = PageHome(wrapper=mock_nrobo)
    page.search("pytest")

    mock_nrobo.logger.info.assert_called_with("Search for pytest")
    mock_nrobo.type_into.assert_called_once_with(By.NAME, "q", *"pytest")


def test_page_home_is_visible(mock_nrobo):
    mock_nrobo.is_displayed.return_value = True
    page = PageHome(wrapper=mock_nrobo)

    assert page.is_page_visible() is True
    mock_nrobo.is_displayed.assert_called_once_with(By.NAME, "q")

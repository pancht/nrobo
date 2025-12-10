from unittest.mock import MagicMock

from nrobo.pages.base_page import BasePage


def test_base_page_initializes_all_attributes():
    """
    Covers all lines in BasePage.__init__().
    Ensures that page, driver, and logger are properly set from SeleniumWrapper mock.
    """
    # Arrange: create a mock SeleniumWrapper
    mock_driver = MagicMock(name="MockWebDriver")
    mock_logger = MagicMock(name="MockLogger")

    mock_page = MagicMock(name="MockSeleniumWrapper")
    mock_page.driver = mock_driver
    mock_page.logger = mock_logger

    # Act: instantiate BasePage
    base_page = BasePage(page=mock_page)

    # Assert: all attributes correctly assigned
    assert base_page.page is mock_page
    assert base_page.driver is mock_driver
    assert base_page.logger is mock_logger

    # Bonus: ensure that attributes exist
    assert hasattr(base_page, "page")
    assert hasattr(base_page, "driver")
    assert hasattr(base_page, "logger")

    # And the class-level docstring exists (for coverage completeness)
    assert "Base class for all Page Object Model" in BasePage.__doc__

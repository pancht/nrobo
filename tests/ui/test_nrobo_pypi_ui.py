from selenium.webdriver.common.by import By

from nrobo.selenium_wrappers.nrobo_selenium_wrapper import (  # noqa: E501
    NRoboSeleniumWrapperClass,
)
from nrobo.templates.home_page import PageHome


def test_nrobo_pypi_page(nrobo: NRoboSeleniumWrapperClass):  # noqa: E501
    nrobo_pypi_page = PageHome(nrobo)
    url = "https://pypi.org/project/nrobo/"
    nrobo_pypi_page.logger.info(f"Open {url}")
    nrobo_pypi_page.get(url)
    nrobo_pypi_page.wait_for_element_to_be_present(By.XPATH, "//h1[@class='package-header__name']")
    assert nrobo_pypi_page.is_page_visible()

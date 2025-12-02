from nrobo.selenium_wrappers.nrobo_selenium_wrapper import (  # noqa: E501
    NRoboSeleniumWrapperClass,
)
from nrobo.templates.home_page import PageHome


def test_nrobo_pypi_page(nrobo: NRoboSeleniumWrapperClass):  # noqa: E501
    nrobo_pypi_page = PageHome(nrobo)
    url = "https://pypi.org/project/nrobo/"
    nrobo.logger.info(f"Open {url}")
    nrobo_pypi_page.get(url)
    nrobo.wait_for_page_to_be_loaded()
    assert nrobo_pypi_page.is_page_visible()

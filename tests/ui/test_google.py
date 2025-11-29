from nrobo.selenium_wrappers.nrobo_selenium_wrapper import (  # noqa: E501
    NRoboSeleniumWrapperClass,
)
from nrobo.templates.home_page import PageHome


def test_google_home_loading(nrobo: NRoboSeleniumWrapperClass):  # noqa: E501
    google_home_page = PageHome(nrobo)
    url = "https://www.google.com"
    nrobo.logger.info(f"Open {url}")
    google_home_page.get(url)
    assert google_home_page.is_page_visible()

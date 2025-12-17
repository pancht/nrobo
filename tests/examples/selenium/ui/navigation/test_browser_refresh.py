import pytest

from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper

website = "https://the-internet.herokuapp.com/"
expected_header = "Welcome to the-internet"


@pytest.mark.example
def test_browser_refresh(page: SeleniumWrapper):
    page.logger.info(f"Go to site: {website}")
    page.goto(website)

    page.logger.info("Refresh browser")
    page.refresh()

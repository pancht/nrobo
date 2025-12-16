import pytest

from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper

website = "https://the-internet.herokuapp.com/"
expected_header = "Welcome to the-internet"


@pytest.mark.example
def test_open_url_using_goto(page: SeleniumWrapper):
    page.logger.info(f"Go to site: {website}")
    page.goto(website)
    page.logger.info(f"Verify that H1 heading with text, {expected_header}, is present")
    page.locator("#content > h1").should_have_exact_text(expected_header)


@pytest.mark.example
def test_open_url_using_get(page: SeleniumWrapper):
    page.logger.info(f"Go to site: {website}")
    page.get(website)
    page.logger.info(f"Verify that H1 heading with text, {expected_header}, is present")
    page.locator("#content > h1").should_have_exact_text(expected_header)

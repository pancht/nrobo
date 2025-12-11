import pytest

from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper

website = "https://the-internet.herokuapp.com/"
expected_header = "Welcome to the-internet"


@pytest.mark.example
def test_css_selector_strategies(page: SeleniumWrapper):
    page.logger.info(f"Go to site: {website}")
    page.goto(website)

    page.locator("h1").should_have_exact_text(expected_header)
    # page.locator("#content > h1").should_have_exact_text(expected_header)
    # page.locator("#content > ul").locator("li").should_have_text("A/B")
    # page.locator("//ul").locator("li").should_have_text("A/B")

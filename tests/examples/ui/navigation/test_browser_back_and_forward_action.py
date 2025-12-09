import pytest

from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper

website = "https://the-internet.herokuapp.com/"
expected_header = "Welcome to the-internet"


@pytest.mark.example
def test_browser_back_action(page: SeleniumWrapper):
    page.logger.info(f"Go to site: {website}")
    page.goto(website)

    page.logger.info("Click on A/B testing link")
    page.locator("link=A/B Testing").click()

    page.logger.info("Perform browser back action")
    page.back()
    page.locator("#content > h1").should_have_exact_text(expected_header)

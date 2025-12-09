import pytest

from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper
from nrobo.templates.home_page import PageHome


@pytest.mark.parametrize("fixture_name", ["nrobo", "page"])
def test_nrobo_pypi_page(request, fixture_name, logger):
    wrapper: SeleniumWrapper = request.getfixturevalue(fixture_name)
    page = PageHome(wrapper)

    page.get("https://pypi.org/project/nrobo/")

    # Assertions
    page.locator("//h1[@class='package-header__name']").is_displayed()
    page.locator('//*[@class="project-description"]/h1').should_have_text(
        "nRobo — Next-Gen Test Automation for Selenium (with Playwright Superpowers)"
    )

    # Feature list
    features = page.locator("//h2[contains(text(),'Features')]/following-sibling::ul[1]/li").all()

    logger.info("Features Found: %s", features)
    logger.info("First Feature: %s", features[0].text)

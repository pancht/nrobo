from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper
from nrobo.templates.home_page import PageHome


def test_nrobo_pypi_page(nrobo: SeleniumWrapper, logger):  # noqa: E501
    nrobo_pypi_page = PageHome(nrobo)
    url = "https://pypi.org/project/nrobo/"
    nrobo_pypi_page.get(url)
    # nrobo_pypi_page.wait_for_element_to_be_present(By.XPATH, "//h1[@class='package-header__name']")
    nrobo_pypi_page.locator("//h1[@class='package-header__name']").is_displayed()
    nrobo_pypi_page.locator('//*[@class="project-description"]/h1').should_have_text(
        "nrobo – NextGen Test Automation Framework"
    )
    feature_list = nrobo_pypi_page.locator(
        "//h2[contains(text(),'Features')]/following-sibling::ul[1]/li"
    ).all()
    logger.info(feature_list)
    logger.info(feature_list[0].text)

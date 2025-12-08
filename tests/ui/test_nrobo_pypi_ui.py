from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper
from nrobo.templates.home_page import PageHome


def test_nrobo_pypi_page(nrobo: SeleniumWrapper):  # noqa: E501
    nrobo_pypi_page = PageHome(nrobo)
    url = "https://pypi.org/project/nrobo/"
    nrobo_pypi_page.logger.info(f"Open {url}")
    nrobo_pypi_page.get(url)
    # nrobo_pypi_page.wait_for_element_to_be_present(By.XPATH, "//h1[@class='package-header__name']")
    nrobo_pypi_page.locator("//h1[@class='package-header__name']").is_displayed()
    nrobo.logger.info(nrobo_pypi_page.locator('//*[@class="project-description"]/h1').text)
    nrobo_pypi_page.locator('//*[@class="project-description"]/h1').click()

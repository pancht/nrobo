from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper


def test_open_url_using_goto(page: SeleniumWrapper):
    page.goto("https://the-internet.herokuapp.com/")
    page.locator("#content > h1").should_have_exact_text("Welcome to the-internet")


def test_open_url_using_get(page: SeleniumWrapper):
    page.get("https://the-internet.herokuapp.com/")
    page.locator("#content > h1").should_have_exact_text("Welcome to the-internet")

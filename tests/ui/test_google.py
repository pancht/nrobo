from nrobo.templates.home_page import PageHome


def test_google_home_loading(nrobo_wrapper):
    google_home_page = PageHome(nrobo_wrapper)
    google_home_page.get("https://www.google.com")

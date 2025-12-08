from unittest.mock import MagicMock

from nrobo.locators.web_element_protocol import WebElementProtocol


# ---------------------------------------------------------------------------
# A single clean Fake implementation of WebElementProtocol
# ---------------------------------------------------------------------------
class FakeWebElement:
    # ---- Element Metadata ----
    @property
    def text(self):
        return "hello"

    @property
    def tag_name(self):
        return "div"

    # ---- Layout ----
    @property
    def location(self):
        return {"x": 1}

    @property
    def location_once_scrolled_into_view(self):
        return {"y": 2}

    @property
    def size(self):
        return {"w": 100}

    @property
    def rect(self):
        return {"w": 100, "h": 50}

    # ---- Core Actions ----
    def click(self):
        pass

    def clear(self):
        pass

    def submit(self):
        pass

    def send_keys(self, *value):
        pass

    # ---- State Queries ----
    def is_displayed(self):
        return True

    def is_enabled(self):
        return True

    def is_selected(self):
        return False

    # ---- DOM / CSS ----
    def get_attribute(self, name):
        return None

    def get_property(self, name):
        return None

    def get_dom_attribute(self, name):
        return None

    def get_dom_property(self, name):
        return None

    def value_of_css_property(self, prop):
        return "blue"

    # ---- Screenshots ----
    def screenshot(self, filename):
        return True

    def screenshot_as_png(self):
        return b"png"

    def screenshot_as_base64(self):
        return "base64"

    # ---- Children ----
    def find_element(self, by, value):
        return self

    def find_elements(self, by, value):
        return [self]


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------


def test_fake_webelement_satisfies_protocol():
    el = FakeWebElement()
    assert isinstance(el, WebElementProtocol)


def test_magicmock_with_spec_satisfies_protocol():
    el = MagicMock(spec=WebElementProtocol)

    # instance attribute overrides
    el.text = "txt"
    el.tag_name = "tag"

    assert isinstance(el, WebElementProtocol)
    # ensure required methods exist
    el.click()
    el.clear()
    el.send_keys("A")


def test_protocol_rejects_simple_magicmock():
    bad = MagicMock()
    assert not isinstance(bad, WebElementProtocol)


def test_protocol_rejects_incomplete_custom_class():
    class Incomplete:
        pass

    assert not isinstance(Incomplete(), WebElementProtocol)

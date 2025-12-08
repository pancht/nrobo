from typing import Any, List

from nrobo.locators.web_element_protocol import WebElementProtocol


class FakeWebElement(WebElementProtocol):
    def __init__(self):
        # Data fields
        self._text = "hello"
        self._tag_name = "div"
        self._location = {"x": 0, "y": 0}
        self._location_once_scrolled_into_view = {"x": 0, "y": 0}
        self._size = {"width": 10, "height": 10}
        self._rect = {"width": 10, "height": 10}

    # --- Properties ---
    @property
    def text(self) -> str:
        return self._text

    @property
    def tag_name(self) -> str:
        return self._tag_name

    @property
    def location(self) -> dict:
        return self._location

    @property
    def location_once_scrolled_into_view(self) -> dict:
        return self._location_once_scrolled_into_view

    @property
    def size(self) -> dict:
        return self._size

    @property
    def rect(self) -> dict:
        return self._rect

    # --- Core Actions ---
    def click(self) -> None:
        pass

    def clear(self) -> None:
        pass

    def submit(self) -> None:
        pass

    def send_keys(self, *value: Any) -> None:
        pass

    # --- State Queries ---
    def is_displayed(self) -> bool:
        return True

    def is_enabled(self) -> bool:
        return True

    def is_selected(self) -> bool:
        return False

    # --- Metadata ---
    def get_attribute(self, name: str) -> Any:
        return None

    def get_property(self, name: str) -> Any:
        return None

    def get_dom_attribute(self, name: str) -> Any:
        return None

    def get_dom_property(self, name: str) -> Any:
        return None

    def value_of_css_property(self, property_name: str) -> str:
        return ""

    # --- Screenshots ---
    def screenshot(self, filename: str) -> bool:
        return True

    def screenshot_as_png(self) -> bytes:
        return b""

    def screenshot_as_base64(self) -> str:
        return ""

    # --- Children ---
    def find_element(self, by: str, value: str) -> "WebElementProtocol":
        return FakeWebElement()

    def find_elements(self, by: str, value: str) -> List["WebElementProtocol"]:
        return [FakeWebElement()]


def test_webelement_protocol_accepts_valid_object():

    obj = FakeWebElement()

    assert isinstance(obj, WebElementProtocol)


def test_webelement_protocol_rejects_invalid_object():
    class IncompleteElement:
        def click(self):
            pass  # missing many required methods

    obj = IncompleteElement()

    assert not isinstance(obj, WebElementProtocol)


def test_webelement_protocol_accepts_fake_element():
    el = FakeWebElement()
    assert isinstance(el, WebElementProtocol)

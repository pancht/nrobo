# pragma: no cover
from typing import Any, Dict, List, Protocol, runtime_checkable


@runtime_checkable
class WebElementProtocol(Protocol):  # pragma: no cover
    # pragma: no cover

    # ---- Element Metadata ----
    @property
    def text(self) -> str: ...  # noqa: E704
    @property
    def tag_name(self) -> str: ...  # noqa: E704

    # ---- Layout ----
    @property
    def location(self) -> Dict[str, Any]: ...  # noqa: E704
    @property
    def location_once_scrolled_into_view(self) -> Dict[str, Any]: ...  # noqa: E704
    @property
    def size(self) -> Dict[str, Any]: ...  # noqa: E704
    @property
    def rect(self) -> Dict[str, Any]: ...  # noqa: E704

    # ---- Core Actions ----
    def click(self) -> None: ...  # noqa: E704
    def clear(self) -> None: ...  # noqa: E704
    def submit(self) -> None: ...  # noqa: E704
    def send_keys(self, *value: Any) -> None: ...  # noqa: E704

    # ---- State Queries ----
    def is_displayed(self) -> bool: ...  # noqa: E704
    def is_enabled(self) -> bool: ...  # noqa: E704
    def is_selected(self) -> bool: ...  # noqa: E704

    # ---- DOM / CSS ----
    def get_attribute(self, name: str) -> Any: ...  # noqa: E704
    def get_property(self, name: str) -> Any: ...  # noqa: E704
    def get_dom_attribute(self, name: str) -> Any: ...  # noqa: E704
    def get_dom_property(self, name: str) -> Any: ...  # noqa: E704
    def value_of_css_property(self, property_name: str) -> str: ...  # noqa: E704

    # ---- Screenshots ----
    def screenshot(self, filename: str) -> bool: ...  # noqa: E704
    def screenshot_as_png(self) -> bytes: ...  # noqa: E704
    def screenshot_as_base64(self) -> str: ...  # noqa: E704

    # ---- Children ----
    def find_element(self, by: str, value: str) -> "WebElementProtocol": ...  # noqa: E704
    def find_elements(self, by: str, value: str) -> List["WebElementProtocol"]: ...  # noqa: E704

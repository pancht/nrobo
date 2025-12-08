from typing import Protocol, runtime_checkable


@runtime_checkable
class WebElementProtocol(Protocol):
    """Protocol representing Selenium WebElement API for autocomplete + type checking."""

    pass

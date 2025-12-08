# src/nrobo/browser/base_driver.py
from abc import ABC


class BaseDriver(ABC):
    """Abstract driver interface for browser automation engines."""

    pass
    # @abstractmethod
    # def open(self, url: str):
    #     """Open a URL in the browser."""
    #     pass
    #
    # @abstractmethod
    # def click(self, selector: str):
    #     """Click an element by selector."""
    #     pass
    #
    # @abstractmethod
    # def type(self, selector: str, text: str):
    #     """Type text into an input field."""
    #     pass
    #
    # @abstractmethod
    # def get_text(self, selector: str) -> str:
    #     """Get element text."""
    #     pass
    #
    # @abstractmethod
    # def screenshot(self, path: str):
    #     """Capture a screenshot."""
    #     pass
    #
    # @abstractmethod
    # def close(self):
    #     """Close the browser."""
    #     pass

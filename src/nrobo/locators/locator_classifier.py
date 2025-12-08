import re
from enum import Enum


class LocatorType(str, Enum):
    XPATH = "xpath"
    CSS = "css"
    ID = "id"
    NAME = "name"
    PLAYWRIGHT = "playwright"
    SHADOW = "shadow"
    TEXT = "text"
    HAS_TEXT = "has_text"
    HAS = "has"
    UNKNOWN = "unknown"


class LocatorClassifier:
    @staticmethod
    def detect(locator: str) -> LocatorType:
        locator = locator.strip()

        # Explicit playwright-style locators
        if "=" in locator and locator.split("=")[0] in {"text", "role", "label"}:
            return LocatorType.PLAYWRIGHT

        # XPath: starts with / or .//
        if locator.startswith(("/", ".//", "//", "..")) or "(@" in locator:
            return LocatorType.XPATH

        # CSS: contains .class, #id, > child selectors, attributes, or :pseudo
        if re.search(r"[.#>:\[\]=]", locator):
            return LocatorType.CSS

        # Fallback: simple ID or NAME guess (alphanumeric, underscores)
        if re.match(r"^[a-zA-Z0-9_-]+$", locator):
            # This could be id or name — depends on DOM usage
            return LocatorType.ID

        if ">>>" in locator or "shadow::" in locator:
            return LocatorType.SHADOW

        if locator.startswith("text="):
            return LocatorType.TEXT

        # quoted literal text e.g. "Login"
        if (locator.startswith('"') and locator.endswith('"')) or (
            locator.startswith("'") and locator.endswith("'")
        ):
            return LocatorType.TEXT

        if ":has-text(" in locator:
            return LocatorType.HAS_TEXT

        if ":has(" in locator:
            return LocatorType.HAS

        return LocatorType.UNKNOWN

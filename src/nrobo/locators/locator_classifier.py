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
    PSEUDO = "pseudo"
    JS_TEXT = "js_text"
    UNKNOWN = "unknown"


class LocatorClassifier:
    @staticmethod
    def detect(locator: str) -> LocatorType:
        locator = locator.strip()

        # --------------------------------------
        # PLAYWRIGHT-style selectors: text= link= role= label= etc.
        # --------------------------------------
        prefix = locator.split("=", 1)[0]
        if "=" in locator and prefix in {"text", "role", "label", "link", "partial-text"}:
            return LocatorType.PLAYWRIGHT

        # TEXT explicit
        if locator.startswith("text="):
            return LocatorType.TEXT  # # pragma: no cover

        # XPATH
        if locator.startswith(("/", ".//", "//", "..")) or "(@" in locator:
            return LocatorType.XPATH

        # SHADOW
        if ">>>" in locator or "shadow::" in locator:
            return LocatorType.SHADOW

        # QUOTED TEXT
        if (locator.startswith('"') and locator.endswith('"')) or (
            locator.startswith("'") and locator.endswith("'")
        ):
            return LocatorType.TEXT

        # HAS-TEXT
        if ":has-text(" in locator:
            return LocatorType.HAS_TEXT

        # HAS
        if ":has(" in locator:
            return LocatorType.HAS

        # PSEUDO (Playwright-style filters)
        if any(
            p in locator
            for p in (":visible", ":hidden", ":enabled", ":disabled", ":checked", ":not(")
        ):
            return LocatorType.PSEUDO

        # CSS fallback (contains CSS tokens)
        if re.search(r"[.#>:\[\]=]", locator):
            return LocatorType.CSS

        # ID (simple alphanumerics)
        if re.match(r"^[a-zA-Z0-9_-]+$", locator):
            return LocatorType.ID

        return LocatorType.UNKNOWN

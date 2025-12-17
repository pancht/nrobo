import re
from enum import Enum

HTML_TAGS = {
    "a",
    "abbr",
    "address",
    "area",
    "article",
    "aside",
    "audio",
    "b",
    "base",
    "bdi",
    "bdo",
    "blockquote",
    "body",
    "br",
    "button",
    "canvas",
    "caption",
    "cite",
    "code",
    "col",
    "colgroup",
    "data",
    "datalist",
    "dd",
    "del",
    "details",
    "dfn",
    "dialog",
    "div",
    "dl",
    "dt",
    "em",
    "embed",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hr",
    "html",
    "i",
    "iframe",
    "img",
    "input",
    "ins",
    "kbd",
    "label",
    "legend",
    "li",
    "link",
    "main",
    "map",
    "mark",
    "meta",
    "meter",
    "nav",
    "noscript",
    "object",
    "ol",
    "optgroup",
    "option",
    "output",
    "p",
    "param",
    "picture",
    "pre",
    "progress",
    "q",
    "rb",
    "rp",
    "rt",
    "rtc",
    "ruby",
    "s",
    "samp",
    "script",
    "section",
    "select",
    "slot",
    "small",
    "source",
    "span",
    "strong",
    "style",
    "sub",
    "summary",
    "sup",
    "svg",
    "table",
    "tbody",
    "td",
    "template",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "time",
    "title",
    "tr",
    "track",
    "u",
    "ul",
    "var",
    "video",
    "wbr",
}


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
        if locator is None:
            return LocatorType.UNKNOWN

        locator = locator.strip()

        # EMPTY / WHITESPACE → UNKNOWN
        if locator == "":
            return LocatorType.UNKNOWN

        # --------------------------------------
        # PLAYWRIGHT selectors: text= role= label= etc.
        # --------------------------------------
        prefix = locator.split("=", 1)[0]
        if "=" in locator and prefix in {"text", "role", "label", "link", "partial-text"}:
            return LocatorType.PLAYWRIGHT

        # TEXT explicit form
        if locator.startswith("text="):
            return LocatorType.TEXT  # pragma: no cover

        # QUOTED TEXT
        if (locator.startswith('"') and locator.endswith('"')) or (
            locator.startswith("'") and locator.endswith("'")
        ):
            return LocatorType.TEXT

        # --------------------------------------
        # XPATH rules
        # --------------------------------------
        if locator.startswith(("/", ".//", "./", "//", "..")):
            return LocatorType.XPATH

        # (//div)[1]
        if locator.startswith("(") and "//" in locator:
            return LocatorType.XPATH

        # contains XPath-style attribute check
        if "(@" in locator:
            return LocatorType.XPATH  # pragma: no cover

        # --------------------------------------
        # SHADOW DOM (Playwright-style)
        # --------------------------------------
        # Supports:
        #   ">>>" deep shadow
        #   " >> " shallow shadow
        #   "shadow::" CSS shadow pseudo-element
        if ">>>" in locator or " >> " in locator or "shadow::" in locator:
            return LocatorType.SHADOW

        # --------------------------------------
        # :has-text(), :has()
        # --------------------------------------
        if ":has-text(" in locator:
            return LocatorType.HAS_TEXT

        if ":has(" in locator:
            return LocatorType.HAS

        # --------------------------------------
        # PSEUDO selectors
        # --------------------------------------
        if any(
            p in locator
            for p in (":visible", ":hidden", ":enabled", ":disabled", ":checked", ":not(")
        ):
            return LocatorType.PSEUDO

        # HTML TAGS set-based exact match
        if locator in HTML_TAGS:
            return LocatorType.CSS

        # --------------------------------------
        # GARBAGE DETECTOR — fixes "!@#$%^" and "123 @bad"
        # --------------------------------------
        # Case 1: only symbols → UNKNOWN
        if re.fullmatch(r"[^\w\s]+", locator):
            return LocatorType.UNKNOWN

        # Case 2: contains illegal characters like "@"
        if "@" in locator:
            return LocatorType.UNKNOWN

        # --------------------------------------
        # CSS SELECTOR FALLBACK
        # --------------------------------------
        if re.search(r"[.#>\[\]=:]", locator):
            return LocatorType.CSS

        # --------------------------------------
        # ID fallback
        # --------------------------------------
        if re.fullmatch(r"[A-Za-z0-9_-]+", locator):
            return LocatorType.ID

        # NOTHING MATCHED
        return LocatorType.UNKNOWN

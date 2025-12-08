from __future__ import annotations

import random
import re
import time
from typing import Any, Callable, List

from nrobo.locators.web_element_protocol import WebElementProtocol


class LocatorCollection:
    """A Playwright-style collection of Locator objects."""

    def __init__(self, locators: List["Locator"]):  # noqa: F821
        self.locators = locators

    # --------------------------------------------------------
    # Basic collection behavior
    # --------------------------------------------------------
    def __len__(self):
        return len(self.locators)

    def __getitem__(self, index):
        return self.locators[index]

    def __iter__(self):
        return iter(self.locators)

    # --------------------------------------------------------
    # Selection helpers
    # --------------------------------------------------------
    def nth(self, index: int) -> "Locator":  # noqa: F821
        return self.locators[index]

    def first(self) -> "Locator":  # noqa: F821 # noqa: F821
        if not self.locators:
            raise AssertionError("No elements in LocatorCollection")
        return self.locators[0]

    def last(self) -> "Locator":  # noqa: F821
        if not self.locators:
            raise AssertionError("No elements in LocatorCollection")  # pragma: no cover
        return self.locators[-1]

    def count(self) -> int:
        return len(self.locators)  # pragma: no cover

    # --------------------------------------------------------
    # Core filtering (delegates to each Locator internally)
    # --------------------------------------------------------
    def filter(
        self,
        has_text: str | None = None,
        has_not_text: str | None = None,
        has_attribute: tuple[str, str] | None = None,
        has_regex: str | None = None,
        has: Callable[[WebElementProtocol], bool] | None = None,
    ) -> "LocatorCollection":

        regex = re.compile(has_regex) if has_regex else None
        results = []

        for loc in self.locators:
            try:
                el = loc.wrapper._resolve(loc)
                text = el.text or ""
            except Exception:  # nosec: B112   # pragma: no cover
                continue  # pragma: no cover

            if has_text and has_text not in text:
                continue
            if has_not_text and has_not_text in text:
                continue

            if has_attribute:
                name, val = has_attribute
                if (el.get_attribute(name) or "").strip() != val.strip():
                    continue

            if regex and not regex.search(text):
                continue

            if has and not has(el):
                continue

            results.append(loc)

        return LocatorCollection(results)

    # --------------------------------------------------------
    # Utility helpers
    # --------------------------------------------------------
    def to_texts(self) -> List[str]:
        """Return list of element.text values."""
        results = []
        for loc in self.locators:
            el = loc.wrapper._resolve(loc)
            results.append(el.text or "")
        return results

    def to_attributes(self, name: str) -> List[str]:
        """Return list of attribute values for all elements."""
        results = []
        for loc in self.locators:
            el = loc.wrapper._resolve(loc)
            results.append(el.get_attribute(name))
        return results

    def map(self, func: Callable[[WebElementProtocol], Any]) -> List[Any]:
        """Apply a function to each WebElement and return list of results."""
        output = []
        for loc in self.locators:
            el = loc.wrapper._resolve(loc)
            output.append(func(el))
        return output

    def for_each(self, func: Callable[[Locator], None]) -> None:  # noqa: F821
        """Call a function for each Locator (not raw element)."""
        for loc in self.locators:
            func(loc)

    def click_each(self) -> None:
        """Click all elements."""
        for loc in self.locators:
            loc.click()

    # --------------------------------------------------------
    # Assertion helpers
    # --------------------------------------------------------
    def should_have_count(self, expected: int) -> "LocatorCollection":
        count = len(self.locators)
        if count != expected:
            raise AssertionError(f"Expected {expected} elements, found {count}")
        return self

    def texts_contain(self, substring: str) -> "LocatorCollection":
        for loc in self.locators:
            el = loc.wrapper._resolve(loc)
            if substring not in (el.text or ""):
                raise AssertionError(
                    f"Expected all elements to contain {substring!r}, but got {el.text!r}"
                )
        return self

    def all_match(self, func: Callable[[WebElementProtocol], bool]) -> bool:
        """Return True only if all elements satisfy the condition."""
        for loc in self.locators:
            el = loc.wrapper._resolve(loc)
            if not func(el):
                return False  # pragma: no cover
        return True

    def any_match(self, func: Callable[[WebElementProtocol], bool]) -> bool:
        """Return True if any element satisfies the condition."""
        for loc in self.locators:
            el = loc.wrapper._resolve(loc)
            if func(el):
                return True
        return False

    # --------------------------------------------------------
    # Sorting helpers
    # --------------------------------------------------------
    def sort_by_text(self) -> "LocatorCollection":
        sorted_locs = sorted(
            self.locators, key=lambda loc: (loc.wrapper._resolve(loc).text or "").strip()
        )
        return LocatorCollection(sorted_locs)

    def sorted_by_attribute(self, name: str) -> "LocatorCollection":
        sorted_locs = sorted(
            self.locators, key=lambda loc: (loc.wrapper._resolve(loc).get_attribute(name) or "")
        )
        return LocatorCollection(sorted_locs)

    # --------------------------------------------------------
    # Visibility / Enabled filters
    # --------------------------------------------------------
    def filter_visible(self) -> "LocatorCollection":
        results = []
        for loc in self.locators:
            el = loc.wrapper._resolve(loc)
            if el.is_displayed():
                results.append(loc)
        return LocatorCollection(results)

    def filter_enabled(self) -> "LocatorCollection":
        results = []
        for loc in self.locators:
            el = loc.wrapper._resolve(loc)
            if el.is_enabled():
                results.append(loc)
        return LocatorCollection(results)

    def reverse(self) -> "LocatorCollection":
        return LocatorCollection(list(reversed(self.locators)))

    def shuffle(self) -> "LocatorCollection":
        locs = self.locators[:]
        random.shuffle(locs)
        return LocatorCollection(locs)

    def random(self) -> "Locator":  # noqa: F821
        if not self.locators:
            raise AssertionError("Cannot pick random() from empty LocatorCollection")
        return random.choice(self.locators)  # nosec: B311

    def wait_for_count(self, expected: int, timeout=5) -> "LocatorCollection":
        end_time = time.time() + timeout

        while time.time() < end_time:
            current = len(self.locators)
            if current == expected:
                return self
            time.sleep(0.2)

        raise AssertionError(f"Timeout waiting for count={expected}, current={len(self.locators)}")

    def exclude(self, other: "LocatorCollection") -> "LocatorCollection":
        others = {(loc.by, loc.value, loc.index) for loc in other.locators}
        filtered = [loc for loc in self.locators if (loc.by, loc.value, loc.index) not in others]
        return LocatorCollection(filtered)

    def difference(self, other: "LocatorCollection") -> "LocatorCollection":
        return self.exclude(other)

    def intersection(self, other: "LocatorCollection") -> "LocatorCollection":
        other_set = {(loc.by, loc.value, loc.index) for loc in other.locators}
        shared = [loc for loc in self.locators if (loc.by, loc.value, loc.index) in other_set]
        return LocatorCollection(shared)

    def union(self, other: "LocatorCollection") -> "LocatorCollection":
        seen = set()
        combined = []

        for loc in self.locators + other.locators:
            key = (loc.by, loc.value, loc.index)
            if key not in seen:
                seen.add(key)
                combined.append(loc)

        return LocatorCollection(combined)

    def unique(self) -> "LocatorCollection":
        seen = set()
        unique_list = []

        for loc in self.locators:
            key = (loc.by, loc.value, loc.index)
            if key not in seen:
                seen.add(key)
                unique_list.append(loc)

        return LocatorCollection(unique_list)

    def filter_index(self, predicate: Callable[[int], bool]) -> "LocatorCollection":
        return LocatorCollection([loc for idx, loc in enumerate(self.locators) if predicate(idx)])

    def slice(self, start: int, end: int) -> "LocatorCollection":
        return LocatorCollection(self.locators[start:end])

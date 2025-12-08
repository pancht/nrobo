from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper


class Locator:
    def __init__(self, wrapper: SeleniumWrapper, locator: str):
        self.wrapper = wrapper
        self.locator = locator

    # Internal helper to find element each time
    def _find(self):
        by, value = self.wrapper.resolve_locator(self.locator)
        return self.wrapper.find_element(by, value)

    # 1. click()
    def click(self):
        self._find().click()
        return self  # enable chaining

    # 2. is_displayed()
    def is_displayed(self) -> bool:
        return self._find().is_displayed()

    # 3. text()
    @property
    def text(self) -> str:
        return self._find().text

    # 4. double_click()
    def double_click(self):
        elem = self._find()
        self.wrapper.actions.double_click(elem).perform()
        return self

    # 5. fill()
    def fill(self, value: str):
        elem = self._find()
        elem.clear()
        elem.send_keys(value)
        return self  # chainable

    # 6. press()
    def press(self, key):
        elem = self._find()
        elem.send_keys(key)
        return self

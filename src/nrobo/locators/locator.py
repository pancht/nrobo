from nrobo.selenium_wrappers.selenium_wrapper import SeleniumWrapper


class Locator:
    def __init__(self, wrapper: SeleniumWrapper, locator: str):
        self.wrapper = wrapper
        self.locator = locator

    # Internal helper to find element each time
    def _find(self):
        by, value = self.wrapper.resolve_locator(self.locator)
        return self.wrapper.find_element(by, value)

    def __getattr__(self, name):
        """
        Dynamically wrap Selenium WebElement methods.
        If the method returns None (most Selenium actions),
        return `self` to support chaining.
        """

        elem = self._find()
        attr = getattr(elem, name)

        if callable(attr):

            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                # Selenium methods return None; convert to self for chaining
                return self if result is None else result

            return wrapper

        return attr

import logging
import time
from abc import ABC
from typing import Optional

from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from nrobo.selenium_wrappers.action_chains import ActionChainsWrapper
from nrobo.selenium_wrappers.base import ELE_WAIT_TIMEOUT
from nrobo.selenium_wrappers.nrobo_types import AnyBy, AnyDriver


class WebElementWrapper(ActionChainsWrapper, ABC):  # pylint: disable=R0904
    """NRobo webelement wrapper class"""

    def __init__(
        self, driver: AnyDriver, logger: logging.Logger
    ):  # pylint: disable=W0246, noqa: E501
        """
        Constructor - NroboSeleniumWrapper

        :param driver: reference to selenium webdriver
        :param logger: reference to logger instance
        """
        super().__init__(driver, logger)

    def tag_name(self, by: AnyBy, value: Optional[str] = None) -> str:
        """This element's ``tagName`` property."""
        return super().find_element(by, value).tag_name

    def text(self, by: AnyBy, value: Optional[str] = None) -> str:
        """The text of the element."""
        return self.find_element(by, value).text

    def click(self, by: AnyBy, value: Optional[str] = None) -> None:
        """Clicks the element."""
        self.find_element(by, value).click()
        self.update_windows(self.window_handles)

    def click_and_wait(
        self, by: AnyBy, value: Optional[str] = None, wait: int = None
    ) -> None:  # noqa: E501
        """Clicks the element."""
        self.find_element(by, value).click()

        if wait is None:
            time.sleep(ELE_WAIT_TIMEOUT)
        elif wait:
            time.sleep(wait)

        self.update_windows(self.window_handles)

    def element_to_be_clickable(self, by: AnyBy, value: Optional[str] = None) -> None:  # noqa: E501
        """
        wait for <wait> seconds mentioned in
          nrobo-config.yaml till the element is clickble.

        :param by:
        :param value:
        :return:
        """

        WebDriverWait(self.driver, ELE_WAIT_TIMEOUT).until(
            expected_conditions.element_to_be_clickable([by, value])
        )
        self.click(by, value)

    def submit(self, by: AnyBy, value: Optional[str] = None):
        """Submits a form."""
        self.find_element(by, value).submit()

    def clear_spl(self, by: AnyBy, value: Optional[str] = None):
        """clear_spl."""
        element = self.find_element(by, value)
        self.action_chain().click(element).send_keys(  # pylint: disable=E1101
            Keys.ARROW_LEFT
        ).double_click(  # pylint: disable=E1101
            self.find_element(by, value)
        ).send_keys(
            Keys.DELETE
        ).perform()
        # self.wait_for_a_while(1)

    def clear(self, by: AnyBy, value: Optional[str] = None) -> None:
        """Clears the text if it's a text entry element."""
        # self.find_element(by, value).clear()
        self.clear_spl(by, value)

    def get_property(
        self, name, by: AnyBy, value: Optional[str] = None
    ) -> str | bool | WebElement | dict:
        """Gets the given property of the element.

        :Args:
            - name - Name of the property to retrieve.

        :Usage:
            ::

                text_length = target_element.get_property("text_length")
        """
        return self.find_element(by, value).get_property(name)

    def get_dom_attribute(self, name, by: AnyBy, value: Optional[str] = None) -> str:  # noqa: E501
        """Gets the given attribute of the element. Unlike
        :func:`~selenium.webdriver.remote.BaseWebElement.get_attribute`, this
        method only returns attributes declared in the element's HTML markup.

        :Args:
            - name - Name of the attribute to retrieve.

        :Usage:
            ::

                text_length = target_element.get_dom_attribute("class")
        """
        return self.find_element(by, value).get_dom_attribute(name)

    def get_attribute(
        self, name, by: AnyBy, value: Optional[str] = None
    ) -> str | None:  # noqa: E501
        """Gets the given attribute or property of the element.

        This method will first try to return the value of a property with the
        given name. If a property with that name doesn't exist, it returns the
        value of the attribute with the same name. If there's no attribute with
        that name, ``None`` is returned.

        Values which are considered truthy, that is equals "true" or "false",
        are returned as booleans.  All other non-``None`` values are returned
        as strings.  For attributes or properties which do not exist, ``None``
        is returned.

        To obtain the exact value of the attribute or property,
        use :func:`~selenium.webdriver.remote.
                    BaseWebElement.get_dom_attribute` or
        :func:`~selenium.webdriver.remote.
                    BaseWebElement.get_property` methods respectively.

        :Args:
            - name - Name of the attribute/property to retrieve.

        Example::

            # Check if the "active" CSS class is applied to an element.
            is_active = "active" in target_element.get_attribute("class")
        """
        return self.find_element(by, value).get_attribute(name)

    def is_selected(self, by: AnyBy, value: Optional[str] = None) -> bool:
        """Returns whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.
        """

        try:
            return self.find_element(by, value).is_selected()
        except Exception:  # pylint: disable=W0718
            return False

    def is_enabled(self, by: AnyBy, value: Optional[str] = None) -> bool:
        """Returns whether the element is enabled."""

        try:
            return self.find_element(by, value).is_enabled()
        except Exception:  # pylint: disable=W0718
            return False

    def send_keys(  # pylint: disable=W1113
        self, by: AnyBy, value: Optional[str] = None, *text
    ) -> None:  # pylint: disable=W1113
        """Simulates typing into the element.

        :Args:
            - text - A string for typing, or setting form fields.  For setting
              file inputs, this could be a local file path.

        Use this to send simple key events or to fill out form fields::

            form_textfield = driver.find_element(By.NAME, 'username')
            form_textfield.send_keys("admin")

        This can also be used to set file inputs.

        ::

            file_input = driver.find_element(By.NAME, 'profilePic')
            file_input.send_keys("path/to/profilepic.gif")
            # Generally it's better to wrap the file path in one of the methods
            # in os.path to return the actual path to support cross OS testing.
            # file_input.send_keys(os.path.abspath("path/to/profilepic.gif"))
        """
        self.find_element(by, value).send_keys(text)

    def shadow_root(self, by: AnyBy, value: Optional[str] = None) -> ShadowRoot:  # noqa: E501
        """Returns a shadow root of the element if there is one or an error.
        Only works from Chromium 96, Firefox 96, and Safari 16.4 onwards.

        :Returns:
          - ShadowRoot object or
          - NoSuchShadowRoot - if no shadow root was attached to element
        """
        return self.find_element(by, value).shadow_root

    # RenderedWebElement Items
    def is_displayed(self, by: AnyBy, value: Optional[str] = None) -> bool:  # noqa: E501
        """Whether the element is visible to a user."""
        try:
            return self.driver.find_element(by, value).is_displayed()
        except NoSuchElementException:
            return False

    def location_once_scrolled_into_view(
        self, by: AnyBy, value: Optional[str] = None
    ) -> dict:  # noqa: E501
        """THIS PROPERTY MAY CHANGE WITHOUT WARNING. Use this to discover where
        on the screen an element is so that we can click it. This method should
        cause the element to be scrolled into view.

        Returns the top lefthand corner location on the screen, or zero
        coordinates if the element is not visible.
        """
        return self.find_element(by, value).location_once_scrolled_into_view

    def size(self, by: AnyBy, value: Optional[str] = None) -> dict:
        """The size of the element."""
        return self.find_element(by, value).size

    def value_of_css_property(
        self, property_name, by: AnyBy, value: Optional[str] = None
    ) -> str:  # noqa: E501
        """The value of a CSS property."""
        return self.find_element(by, value).value_of_css_property(property_name)  # noqa: E501

    def location(self, by: AnyBy, value: Optional[str] = None) -> dict:  # noqa: E501
        """The location of the element in the renderable canvas."""
        return self.find_element(by, value).location

    def rect(self, by: AnyBy, value: Optional[str] = None) -> dict:  # noqa: E501
        """A dictionary with the size and location of the element."""
        return self.find_element(by, value).rect

    def aria_role(self, by: AnyBy, value: Optional[str] = None) -> str:  # noqa: E501
        """Returns the ARIA role of the current web element."""
        return self.find_element(by, value).aria_role

    def accessible_name(self, by: AnyBy, value: Optional[str] = None) -> str:  # noqa: E501
        """Returns the ARIA Level of the current webelement."""
        return self.find_element(by, value).accessible_name

    def screenshot_as_base64(self, by: AnyBy, value: Optional[str] = None) -> str:  # noqa: E501
        """Gets the screenshot of the current element as a base64 encoded
        string.

        :Usage:
            ::

                img_b64 = element.screenshot_as_base64
        """
        return self.find_element(by, value).screenshot_as_base64

    def screenshot_as_png(self, by: AnyBy, value: Optional[str] = None) -> bytes:  # noqa: E501
        """Gets the screenshot of the current element as a binary data.

        :Usage:
            ::

                element_png = element.screenshot_as_png
        """
        return self.find_element(by, value).screenshot_as_png

    def screenshot(self, filename, by: AnyBy, value: Optional[str] = None) -> bool:  # noqa: E501
        """Saves a screenshot of the current element to a PNG image file.
        Returns False if there is any IOError, else returns True. Use full
        paths in your filename.

        :Args:
         - filename: The full path you wish to save your screenshot to. This
           should end with a `.png` extension.

        :Usage:
            ::

                element.screenshot('/Screenshots/foo.png')
        """
        return self.find_element(by, value).screenshot(filename)

    def parent(self, by: AnyBy, value: Optional[str] = None):
        """Internal reference to the WebDriver instance this element was found
        from."""
        return self.find_element(by, value).parent

    def id(self, by: AnyBy, value: Optional[str] = None) -> str:
        """Internal ID used by selenium.

        This is mainly for internal use. Simple use cases such as checking if 2
        webelements refer to the same element, can be done using ``==``::

            if element1 == element2:
                print("These 2 are equal")
        """
        return self.find_element(by, value).id

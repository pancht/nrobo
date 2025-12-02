# nrobo_wrapper.py


import logging
import typing
from abc import ABC

from selenium.common import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.print_page_options import (  # pylint: disable=C0412, C0412 # noqa: E501
    PrintOptions,
)
from selenium.webdriver.common.timeouts import Timeouts
from selenium.webdriver.common.virtual_authenticator import (
    Credential,
    VirtualAuthenticatorOptions,
    required_virtual_authenticator,
)
from selenium.webdriver.remote.file_detector import FileDetector
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from nrobo.selenium_wrappers.nrobo_types import AnyBy, AnyDriver
from nrobo.utils.driver_utils import is_mobile_session

PAGE_LOAD_TIMEOUT = 30
ELE_WAIT_TIMEOUT = 10


class SeleniumWrapperBase(ABC):  # pylint: disable=R0904

    def __init__(
        self, driver: AnyDriver, logger: logging.Logger
    ):  # pylint: disable=W0231,  noqa: E501
        self.driver = driver
        self.logger = logger
        self._windows = {}

    # Following are selenium webdriver wrapper methods and properties
    @property
    def windows(self):
        return self._windows

    @windows.setter
    def windows(self, _windows: {str: str}):
        """windows."""
        self._windows = _windows

    def update_windows(  # pylint: disable=R1710
        self, _window_handles: list[str] = None
    ):  # pylint: disable=R1710
        """update windows."""

        if is_mobile_session(self.driver):
            return

        try:
            __cur_window_handle = self.current_window_handle
        except Exception:  # pylint: disable=W0718
            return

        self.windows = {}
        for _wh in _window_handles:
            # switch to current window
            self.switch_to_window(_wh)
            # add title and handle to windows
            try:
                self.windows[self.title] = _wh
            except UnexpectedAlertPresentException:
                pass

        self.switch_to_window(__cur_window_handle)

        return self.windows

    @property
    def name(self) -> str:
        """Returns the name of the underlying browser for this instance.

        :Usage:
            ::

                name = <obj>.name"""

        return self.driver.name

    def _wait_page_load(self):
        if is_mobile_session(self.driver):
            return

        try:
            # Webdriver implementation of page load timeout
            self.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

            # Custom page load timeout
            WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT).until(  # noqa: E501
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"  # noqa: E501
            )
        except TimeoutException as te:
            self.logger.info(f"Exception: {te}")
        except AttributeError as ae:
            self.logger.info(f"Exception: {ae}")
        # nprint("End of Wait for page load...", style=STYLE.PURPLE4)

    def wait_for_page_to_be_loaded(self):  # pylint: disable=W0612
        self._wait_page_load()

    def get(self, url: str):
        """selenium webdriver wrapper method: get"""

        url = str(url).replace("\\", "\\\\")  # perform replacements
        self.driver.get(url)
        self._wait_page_load()

        self.update_windows(self.window_handles)

    def execute(self, driver_command: str, params: dict = None) -> dict:
        """selenium webdriver wrapper method: execute"""

        self.logger.info("Executing script...")
        return self.driver.execute(driver_command, params)

    @property
    def title(self) -> str:
        """Returns the title of the current page.

        :Usage:
            ::

                title = <obj>.title"""

        return self.driver.title

    @property
    def current_url(self) -> str:
        """Gets the URL of the current page.

        :Usage:
            ::

                <obj>.current_url"""
        return self.driver.current_url

    @property
    def page_source(self) -> str:
        """Gets the source of the current page.

        :Usage:
            ::

               <obj>.page_source"""
        return self.driver.page_source

    def close(self, title: str = None) -> None:
        """selenium webdriver wrapper method: close

        Closes the current window.

        :Usage:
            ::

                driver.close()"""

        if title is None:
            self.driver.close()
            return

        __parent_window_handle_idx = -1

        # Find index of given window/tab in selenium windows list
        for __idx, __wh in enumerate(self.window_handles):
            if __wh == self.windows[title]:
                # Grab parent window handle
                if __idx == 0:
                    __parent_window_handle_idx = 0
                else:
                    __parent_window_handle_idx = __idx - 1

        # switch to given window/tab
        self.switch_to_window(self.windows[title])

        # close given window/tab
        self.driver.close()

        # switch to parent window/tab
        self.switch_to_window(self.window_handles[__parent_window_handle_idx])

        # updated nRoBo windows attribute
        self.update_windows(self.window_handles)

    def quit(self) -> None:
        """Quits the driver and closes every associated window.

        :Usage:
            ::

                driver.quit()"""
        self.driver.quit()

    @property
    def current_window_handle(self) -> str:
        """Returns the handle of the current window.

        :Usage:
            ::

                <obj>.current_window_handle"""
        return self.driver.current_window_handle

    @property
    def window_handles(self) -> typing.List[str]:
        """Returns the handles of all windows within the current session.

        :Usage:
            ::

                <obj>.window_handles"""

        if is_mobile_session(self.driver):
            return []

        return self.driver.window_handles

    def maximize_window(self) -> None:
        """Maximizes the current window that webdriver is using."""

        self.driver.maximize_window()

    def fullscreen_window(self) -> None:
        """Invokes the window manager-specific 'full screen' operation."""

        self.driver.fullscreen_window()

    def minimize_window(self) -> None:
        """Invokes the window manager-specific 'minimize' operation."""

        self.driver.minimize_window()

    def print_page(self, print_options: typing.Optional[PrintOptions] = None) -> str:  # noqa: E501
        """Takes PDF of the current page.

        The driver makes a best effort to return a PDF based on the
        provided parameters."""
        return self.driver.print_page(print_options)

    def switch_to_active_element(self) -> WebElement:
        """Returns the element with focus, or BODY if nothing has focus."""

        return self.driver.switch_to.active_element

    def switch_to_alert(self) -> Alert:
        """Switches focus to an alert on the page."""

        return self.driver.switch_to.alert

    def switch_to_default_content(self) -> None:
        """Switch focus to the default frame."""

        return self.driver.switch_to.default_content()

    def frame(self, frame_reference: typing.Union[str, int, WebElement]) -> None:  # noqa: E501
        """Switches focus to the specified frame,
             by index, name, or webelement.

        :Args:
         - frame_reference: The name of the window to switch to,
          an integer representing the index,
          or a webelement that is an (i)frame to switch to.

        :Usage:
            ::

                switch_to_frame('frame_name')
                switch_to_frame(1)
                switch_to_frame(
                   driver.find_elements(By.TAG_NAME, "iframe")[0])"""

        return self.driver.switch_to.frame(frame_reference)

    def switch_to_new_window(
        self, type_hint: typing.Optional[str] = "window"
    ) -> None:  # noqa: E501
        """Switches to a new top-level browsing context.

        The type hint can be one of "tab" or "window". If not specified the
        browser will automatically select it.

        :Usage:
            ::

                switch_to_new_window('tab')
        """
        self.driver.switch_to.new_window(type_hint)
        self.update_windows(self.window_handles)

    def switch_to_new_tab(self) -> None:
        """
        Create a new tab and switch to it.

        :Usage:
            ::

                switch_to_new_tab()

        :return:
        """
        self.switch_to_new_window("tab")

    def switch_to_parent_frame(self) -> None:
        """Switches focus to the parent context. If the current context is the
        top level browsing context, the context remains unchanged.

        :Usage:
            ::

                switch_to_parent_frame()
        """
        self.driver.switch_to.parent_frame()

    def switch_to_window(self, window_name: str) -> None:
        """Switches focus to the specified window.

        :Args:
         - window_name: The name or window handle of the window to switch to.

        :Usage:
            ::

                switch_to_window('main')
        """
        self.driver.switch_to.window(window_name)

    # Navigation
    def back(self) -> None:
        """Goes one step backward in the browser history.

        :Usage:
            ::

                back()
        """
        self.driver.back()

    def forward(self) -> None:
        """Goes one step forward in the browser history.

        :Usage:
            ::

                forward()
        """
        self.driver.forward()

    def refresh(self) -> None:
        """Refreshes the current page.

        :Usage:
            ::

                refresh()
        """
        self.driver.refresh()

    # Options
    def get_cookies(self) -> typing.List[dict]:
        """Returns a set of dictionaries, corresponding to cookies visible in
        the current session.

        :Usage:
            ::

                get_cookies()
        """
        return self.driver.get_cookies()

    def get_cookie(self, name) -> typing.Optional[typing.Dict]:
        """Get a single cookie by name. Returns the cookie if found, None if
        not.

        :Usage:
            ::

                get_cookie('my_cookie')
        """
        return self.driver.get_cookie(name)

    def delete_cookie(self, name) -> None:
        """Deletes a single cookie with the given name.

        :Usage:
            ::

                delete_cookie('my_cookie')
        """
        self.driver.delete_cookie(name)

    def delete_all_cookies(self) -> None:
        """Delete all cookies in the scope of the session.

        :Usage:
            ::

                delete_all_cookies()
        """
        self.driver.delete_all_cookies()

    def add_cookie(self, cookie_dict) -> None:
        """Adds a cookie to your current session.

        :Args:
         - cookie_dict: A dictionary object,
            with required keys - "name" and "value";
            optional keys - "path", "domain",
            "secure", "httpOnly", "expiry", "sameSite"

        :Usage:
            ::

                add_cookie({'name' : 'foo',
                             'value' : 'bar'})
                add_cookie({'name' : 'foo',
                            'value' : 'bar', 'path' : '/'})
                add_cookie({'name' : 'foo',
                            'value' : 'bar', 'path' : '/', 'secure' : True})
                add_cookie({'name' : 'foo',
                          'value' : 'bar', 'sameSite' : 'Strict'})
        """
        self.driver.add_cookie(cookie_dict)

    # Timeouts
    def implicitly_wait(self, time_to_wait: float) -> None:
        """Sets a sticky timeout to implicitly wait for an element to be found,
        or a command to complete. This method only needs to be called one time
        per session. To set the timeout for calls to execute_async_script, see
        set_script_timeout.

        :Args:
         - time_to_wait: Amount of time to wait (in seconds)

        :Usage:
            ::

                implicitly_wait(30)
        """
        self.driver.implicitly_wait(time_to_wait)

    def set_script_timeout(self, time_to_wait: float) -> None:
        """Set the amount of time that the script should wait during an
        execute_async_script call before throwing an error.

        :Args:
         - time_to_wait: The amount of time to wait (in seconds)

        :Usage:
            ::

                set_script_timeout(30)
        """
        self.driver.set_script_timeout(time_to_wait)

    def set_page_load_timeout(self, time_to_wait: float) -> None:
        """Set the amount of time to wait for a page load to complete before
        throwing an error.

        :Args:
         - time_to_wait: The amount of time to wait

        :Usage:
            ::

                set_page_load_timeout(30)
        """
        self.driver.set_page_load_timeout(time_to_wait)

    @property
    def timeouts(self) -> Timeouts:
        """Get all the timeouts that have been set on the current session.

        :Usage:
            ::

                <obj>.timeouts
        :rtype: Timeout
        """
        return self.driver.timeouts

    @timeouts.setter
    def timeouts(self, timeouts) -> None:
        """Set all timeouts for the session. This will override any previously
        set timeouts.

        :Usage:
            ::
                my_timeouts = Timeouts()
                my_timeouts.implicit_wait = 10
                <obj>.timeouts = my_timeouts
        """
        self.driver.timeouts = timeouts

    def find_element(  # pylint: disable=W0222
        self, by: AnyBy, value: typing.Optional[str] = None
    ) -> WebElement:  # pylint: disable=W0222
        """Find an element given a By strategy and locator.

        :Usage:
            ::

                element = find_element(By.ID, 'foo')

        :rtype: WebElement
        """

        WebDriverWait(self.driver, ELE_WAIT_TIMEOUT).until(
            expected_conditions.presence_of_element_located((by, value))
        )

        return self.driver.find_element(by, value)

    def find_elements(  # pylint: disable=W0222
        self, by: AnyBy, value: typing.Optional[str] = None
    ) -> typing.List[WebElement]:  # pylint: disable=W0222
        """Find elements given a By strategy and locator.

        :Usage:
            ::

                elements = find_elements(By.CLASS_NAME, 'foo')

        :rtype: list of WebElement
        """
        WebDriverWait(self.driver, ELE_WAIT_TIMEOUT).until(
            expected_conditions.presence_of_element_located((by, value))
        )
        return self.driver.find_elements(by, value)

    @property
    def capabilities(self) -> dict:
        """Returns the drivers current capabilities being used."""
        return self.driver.capabilities

    def get_screenshot_as_file(self, filename) -> bool:
        """Saves a screenshot of the current window to a PNG image file.
        Returns False if there is any IOError, else returns True. Use full
        paths in your filename.

        :Args:
         - filename: The full path you wish to save your screenshot to. This
           should end with a `.png` extension.

        :Usage:
            ::

                get_screenshot_as_file('/Screenshots/foo.png')
        """
        return self.driver.get_screenshot_as_file(filename)

    def save_screenshot(self, filename) -> bool:
        """Saves a screenshot of the current window to a PNG image file.
        Returns False if there is any IOError, else returns True. Use full
        paths in your filename.

        :Args:
         - filename: The full path you wish to save your screenshot to. This
           should end with a `.png` extension.

        :Usage:
            ::

                save_screenshot('/Screenshots/foo.png')
        """
        return self.driver.save_screenshot(filename)

    def get_screenshot_as_png(self) -> bytes:
        """Gets the screenshot of the current window as a binary data.

        :Usage:
            ::

                get_screenshot_as_png()
        """
        return self.driver.get_screenshot_as_png()

    def get_screenshot_as_base64(self) -> str:
        """Gets the screenshot of the current window as a base64 encoded string
        which is useful in embedded images in HTML.

        :Usage:
            ::

                get_screenshot_as_base64()
        """
        return self.driver.get_screenshot_as_base64()

    def set_window_size(self, width, height, window_handle: str = "current") -> None:  # noqa: E501
        """Sets the width and height of the current window. (window.resizeTo)

        :Args:
         - width: the width in pixels to set the window to
         - height: the height in pixels to set the window to

        :Usage:
            ::

                set_window_size(800,600)
        """
        self.driver.set_window_size(width, height, window_handle)

    def get_window_size(self, window_handle: str = "current") -> dict:
        """Gets the width and height of the current window.

        :Usage:
            ::

                get_window_size()
        """
        return self.driver.get_window_size(window_handle)

    def set_window_position(self, x, y, window_handle: str = "current") -> dict:  # noqa: E501
        """Sets the x,y position of the current window. (window.moveTo)

        :Args:
         - x: the x-coordinate in pixels to set the window position
         - y: the y-coordinate in pixels to set the window position

        :Usage:
            ::

                set_window_position(0,0)
        """
        return self.driver.set_window_position(x, y, window_handle)

    def get_window_position(self, window_handle="current") -> dict:
        """Gets the x,y position of the current window.

        :Usage:
            ::

                get_window_position()
        """
        return self.driver.get_window_position(window_handle)

    def get_window_rect(self) -> dict:
        """Gets the x, y coordinates of the window as well as height and width
        of the current window.

        :Usage:
            ::

               get_window_rect()
        """
        return self.driver.get_window_rect()

    def set_window_rect(self, x=None, y=None, width=None, height=None) -> dict:
        """Sets the x, y coordinates of the window as well as height and width
        of the current window. This method is only supported for W3C compatible
        browsers; other browsers should use `set_window_position` and
        `set_window_size`.

        :Usage:
            ::

                set_window_rect(x=10, y=10)
                set_window_rect(width=100, height=200)
                set_window_rect(x=10, y=10, width=100, height=200)
        """
        return self.driver.set_window_rect(x, y, width, height)

    @property
    def file_detector(self) -> FileDetector:
        return self.driver.file_detector

    @file_detector.setter
    def file_detector(self, detector) -> None:
        """Set the file detector to be used when sending keyboard input. By
        default, this is set to a file detector that does nothing.

        see FileDetector
        see LocalFileDetector
        see UselessFileDetector

        :Args:
         - detector: The detector to use. Must not be None.
        """
        self.driver.file_detector = detector

    @property
    def orientation(self):
        """Gets the current orientation of the device.

        :Usage:
            ::

                orientation = <obj>.orientation
        """
        return self.driver.orientation

    @orientation.setter
    def orientation(self, value) -> None:
        """Sets the current orientation of the device.

        :Args:
         - value: orientation to set it to.

        :Usage:
            ::

                <obj>.orientation = 'landscape'
        """
        self.driver.orientation = value

    @property
    def log_types(self):
        """Gets a list of the available log types. This only works with w3c
        compliant browsers.

        :Usage:
            ::

                log_types
        """
        return self.driver.log_types

    def get_log(self, log_type):
        """Gets the log for a given log type.

        :Args:
         - log_type: type of log that which will be returned

        :Usage:
            ::

                get_log('browser')
                get_log('driver')
                get_log('client')
                get_log('server')
        """
        return self.driver.get_log(log_type)

    # """
    # Research needed to wrap this method!
    #
    # @asynccontextmanager
    # async def bidi_connection(self):
    # """

    # Virtual Authenticator Methods
    def add_virtual_authenticator(self, options: VirtualAuthenticatorOptions) -> None:  # noqa: E501
        """Adds a virtual authenticator with the given options."""
        self.driver.add_virtual_authenticator(options)

    @property
    def virtual_authenticator_id(self) -> str:
        """Returns the id of the virtual authenticator."""
        return self.driver.virtual_authenticator_id

    @required_virtual_authenticator
    def remove_virtual_authenticator(self) -> None:
        """Removes a previously added virtual authenticator.

        The authenticator is no longer valid after removal, so no
        methods may be called.
        """
        return self.driver.remove_virtual_authenticator

    @required_virtual_authenticator
    def add_credential(self, credential: Credential) -> None:
        """Injects a credential into the authenticator."""
        self.driver.add_credential(credential)

    @required_virtual_authenticator
    def get_credentials(self) -> typing.List[Credential]:
        """Returns the list of credentials owned by the authenticator."""
        return self.driver.get_credentials()

    @required_virtual_authenticator
    def remove_credential(self, credential_id: typing.Union[str, bytearray]) -> None:  # noqa: E501
        """Removes a credential from the authenticator."""
        return self.driver.remove_credential()

    @required_virtual_authenticator
    def remove_all_credentials(self) -> None:
        """Removes all credentials from the authenticator."""
        return self.driver.remove_all_credentials()

    @required_virtual_authenticator
    def set_user_verified(self, verified: bool) -> None:
        """Sets whether the authenticator will simulate success or fail on user
        verification.

        verified: True if the authenticator will
                    pass user verification, False otherwise.
        """
        return self.driver.set_user_verified(verified)

    def get_downloadable_files(self) -> list:
        """Retrieves the downloadable files as a map of file names and their
        corresponding URLs."""
        return self.driver.get_downloadable_files()

    def download_file(self, file_name: str, target_directory: str) -> None:
        """Downloads a file with the specified file name to the target
        directory.

        file_name: The name of the file to download.
        target_directory: The path to the
             directory to save the downloaded file.
        """
        return self.driver.download_file(file_name, target_directory)

    def delete_downloadable_files(self) -> None:
        """Deletes all downloadable files."""
        return self.driver.delete_downloadable_files()

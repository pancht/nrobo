from selenium.common import UnexpectedAlertPresentException

from nrobo.utils.driver_utils import is_mobile_session


class WindowMixin:
    def update_windows(self, _window_handles=None) -> dict:
        if not _window_handles:
            return {}

        if is_mobile_session(self.driver):  # self.driver must exist
            return {}

        try:
            cur_handle = self.current_window_handle
        except Exception as e:
            self.logger.warning(f"Could not get current window handle: {e}")
            return {}

        new_windows = {}
        for wh in _window_handles:
            try:
                self.switch_to_window(wh)
                new_windows[self.title] = wh
            except UnexpectedAlertPresentException:
                self.logger.warning("Alert interrupted window detection.")

        self.switch_to_window(cur_handle)
        self.windows = new_windows
        return new_windows

    def switch_to_window(self, window_name: str) -> None:
        """Switches focus to the specified window.

        :Args:
         - window_name: The name or window handle of the window to switch to.

        :Usage:
            ::

                switch_to_window('main')
        """
        self.driver.switch_to.window(window_name)

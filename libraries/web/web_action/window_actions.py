from .base import Base
from robot.api.deco import keyword, library
import logging

@library
class WindowActions(Base):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    @keyword
    def switch_to_frame(self, element, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Switching to frame: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        self.driver.switch_to.frame(element)
        logging.info(f"{self.__class__.__name__}: Switched to frame successfully: {element_desc}")

    @keyword
    def switch_to_default_content(self):
        logging.info(f"{self.__class__.__name__}: Switching to default content")
        self.driver.switch_to.default_content()
        logging.info(f"{self.__class__.__name__}: Switched to default content successfully")

    @keyword
    def switch_to_window(self, window_handle):
        logging.info(f"{self.__class__.__name__}: Switching to window with handle: {window_handle}")
        self.driver.switch_to.window(window_handle)
        logging.info(f"{self.__class__.__name__}: Switched to window successfully")

    @keyword
    def get_window_handles(self):
        logging.info(f"{self.__class__.__name__}: Getting all window handles")
        handles = self.driver.window_handles
        logging.info(f"{self.__class__.__name__}: Retrieved {len(handles)} window handles")
        return handles

    @keyword
    def close_current_window(self):
        logging.info(f"{self.__class__.__name__}: Closing current window")
        self.driver.close()
        logging.info(f"{self.__class__.__name__}: Current window closed successfully")

    @keyword
    def set_window_size(self, width, height):
        logging.info(f"{self.__class__.__name__}: Setting window size to {width}x{height}")
        self.driver.set_window_size(width, height)
        logging.info(f"{self.__class__.__name__}: Window size set successfully")

    @keyword
    def maximize_window(self):
        logging.info(f"{self.__class__.__name__}: Maximizing window")
        self.driver.maximize_window()
        logging.info(f"{self.__class__.__name__}: Window maximized successfully")

    @keyword
    def minimize_window(self):
        logging.info(f"{self.__class__.__name__}: Minimizing window")
        self.driver.minimize_window()
        logging.info(f"{self.__class__.__name__}: Window minimized successfully")

    @keyword
    def fullscreen_window(self):
        logging.info(f"{self.__class__.__name__}: Setting window to full screen")
        self.driver.fullscreen_window()
        logging.info(f"{self.__class__.__name__}: Window set to full screen successfully")
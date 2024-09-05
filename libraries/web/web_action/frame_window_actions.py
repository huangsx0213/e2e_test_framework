from .base import Base
from .decorators import wait_and_perform
import logging

class FrameWindowActions(Base):
    @wait_and_perform(default_condition="presence")
    def switch_to_frame(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Switching to frame: {element_desc}")
        self.driver.switch_to.frame(element)
        logging.info(f"{self.__class__.__name__}: Switched to frame successfully: {element_desc}")

    def switch_to_default_content(self):
        logging.info(f"{self.__class__.__name__}: Switching to default content")
        self.driver.switch_to.default_content()
        logging.info(f"{self.__class__.__name__}: Switched to default content successfully")

    def switch_to_window(self, window_handle):
        logging.info(f"{self.__class__.__name__}: Switching to window with handle: {window_handle}")
        self.driver.switch_to.window(window_handle)
        logging.info(f"{self.__class__.__name__}: Switched to window successfully")

    def get_window_handles(self):
        logging.info(f"{self.__class__.__name__}: Getting all window handles")
        handles = self.driver.window_handles
        logging.info(f"{self.__class__.__name__}: Retrieved {len(handles)} window handles")
        return handles

    def close_current_window(self):
        logging.info(f"{self.__class__.__name__}: Closing current window")
        self.driver.close()
        logging.info(f"{self.__class__.__name__}: Current window closed successfully")
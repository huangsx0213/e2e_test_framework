from .base import Base
import logging

class BrowserActions(Base):
    def refresh_page(self):
        logging.info(f"{self.__class__.__name__}: Refreshing the current page")
        self.driver.refresh()
        logging.info(f"{self.__class__.__name__}: Page refreshed successfully")

    def go_back(self):
        logging.info(f"{self.__class__.__name__}: Navigating back in browser history")
        self.driver.back()
        logging.info(f"{self.__class__.__name__}: Navigated back successfully")

    def go_forward(self):
        logging.info(f"{self.__class__.__name__}: Navigating forward in browser history")
        self.driver.forward()
        logging.info(f"{self.__class__.__name__}: Navigated forward successfully")

    def get_current_url(self):
        logging.info(f"{self.__class__.__name__}: Getting current URL")
        url = self.driver.current_url
        logging.info(f"{self.__class__.__name__}: Current URL is: '{url}'")
        return url

    def set_window_size(self, width, height):
        logging.info(f"{self.__class__.__name__}: Setting window size to {width}x{height}")
        self.driver.set_window_size(width, height)
        logging.info(f"{self.__class__.__name__}: Window size set successfully")

    def maximize_window(self):
        logging.info(f"{self.__class__.__name__}: Maximizing window")
        self.driver.maximize_window()
        logging.info(f"{self.__class__.__name__}: Window maximized successfully")

    def minimize_window(self):
        logging.info(f"{self.__class__.__name__}: Minimizing window")
        self.driver.minimize_window()
        logging.info(f"{self.__class__.__name__}: Window minimized successfully")

    def fullscreen_window(self):
        logging.info(f"{self.__class__.__name__}: Setting window to full screen")
        self.driver.fullscreen_window()
        logging.info(f"{self.__class__.__name__}: Window set to full screen successfully")
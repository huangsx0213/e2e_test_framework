from .base import Base
from robot.api.deco import keyword, library
import logging

@library
class NavigationActions(Base):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    @keyword
    def open_url(self, url):
        logging.info(f"{self.__class__.__name__}: Opening URL: {url}")
        # self.driver.maximize_window()
        self.driver.get(url)
        logging.info(f"{self.__class__.__name__}: URL opened successfully: {url}")

    @keyword
    def refresh_page(self):
        logging.info(f"{self.__class__.__name__}: Refreshing the current page")
        self.driver.refresh()
        logging.info(f"{self.__class__.__name__}: Page refreshed successfully")

    @keyword
    def go_back(self):
        logging.info(f"{self.__class__.__name__}: Navigating back in browser history")
        self.driver.back()
        logging.info(f"{self.__class__.__name__}: Navigated back successfully")

    @keyword
    def go_forward(self):
        logging.info(f"{self.__class__.__name__}: Navigating forward in browser history")
        self.driver.forward()
        logging.info(f"{self.__class__.__name__}: Navigated forward successfully")

    @keyword
    def get_current_url(self):
        logging.info(f"{self.__class__.__name__}: Getting current URL")
        url = self.driver.current_url
        logging.info(f"{self.__class__.__name__}: Current URL is: '{url}'")
        return url
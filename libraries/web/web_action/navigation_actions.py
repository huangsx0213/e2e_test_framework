from .base import Base
import logging

class NavigationActions(Base):
    def open_url(self, url):
        logging.info(f"{self.__class__.__name__}: Opening URL: {url}")
        # self.driver.maximize_window()
        self.driver.get(url)
        logging.info(f"{self.__class__.__name__}: URL opened successfully: {url}")

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
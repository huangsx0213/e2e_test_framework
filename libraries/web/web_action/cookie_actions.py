from .base import Base
from robot.api.deco import keyword, library
import logging

@library
class CookieActions(Base):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    @keyword
    def add_cookie(self, cookie_dict):
        logging.info(f"{self.__class__.__name__}: Adding cookie: {cookie_dict}")
        self.driver.add_cookie(cookie_dict)
        logging.info(f"{self.__class__.__name__}: Cookie added successfully")

    @keyword
    def get_cookie(self, name):
        logging.info(f"{self.__class__.__name__}: Getting cookie with name: '{name}'")
        cookie = self.driver.get_cookie(name)
        logging.info(f"{self.__class__.__name__}: Cookie retrieved: {cookie}")
        return cookie

    @keyword
    def delete_cookie(self, name):
        logging.info(f"{self.__class__.__name__}: Deleting cookie with name: '{name}'")
        self.driver.delete_cookie(name)
        logging.info(f"{self.__class__.__name__}: Cookie deleted successfully")

    @keyword
    def delete_all_cookies(self):
        logging.info(f"{self.__class__.__name__}: Deleting all cookies")
        self.driver.delete_all_cookies()
        logging.info(f"{self.__class__.__name__}: All cookies deleted successfully")
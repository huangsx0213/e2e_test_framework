from .base import Base
import logging

class CookieActions(Base):
    def add_cookie(self, cookie_dict):
        logging.info(f"{self.__class__.__name__}: Adding cookie: {cookie_dict}")
        self.driver.add_cookie(cookie_dict)
        logging.info(f"{self.__class__.__name__}: Cookie added successfully")

    def get_cookie(self, name):
        logging.info(f"{self.__class__.__name__}: Getting cookie with name: '{name}'")
        cookie = self.driver.get_cookie(name)
        logging.info(f"{self.__class__.__name__}: Cookie retrieved: {cookie}")
        return cookie

    def delete_cookie(self, name):
        logging.info(f"{self.__class__.__name__}: Deleting cookie with name: '{name}'")
        self.driver.delete_cookie(name)
        logging.info(f"{self.__class__.__name__}: Cookie deleted successfully")

    def delete_all_cookies(self):
        logging.info(f"{self.__class__.__name__}: Deleting all cookies")
        self.driver.delete_all_cookies()
        logging.info(f"{self.__class__.__name__}: All cookies deleted successfully")

    def set_cookie(self, cookies: dict):
        # Validate required fields
        for key in ("name", "value"):
            if key not in cookies:
                logging.error(f"{self.__class__.__name__}: Missing required cookie key: '{key}'")
                return

        # Prepare cookie with defaults if not provided
        cookie = {
            "name": cookies["name"],
            "value": cookies["value"],
            "domain": cookies.get("domain", ""),
            "path": cookies.get("path", "/"),
            "secure": cookies.get("secure", True),
            "httpOnly": cookies.get("httpOnly", True),
            "sameSite": cookies.get("sameSite", "None")
        }

        try:
            # Attempt to set the cookie via Chrome DevTools Protocol command
            response = self.driver.execute_cdp_cmd('Network.setCookie', cookie)
            logging.info(f"{self.__class__.__name__}: Set cookie '{cookie['name']}' successfully, response: {response}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to set cookie '{cookie['name']}': {e}")
            return

        # Optionally, verify the cookie was set
        cookie_after = self.driver.get_cookie(cookie["name"])
        logging.info(f"{self.__class__.__name__}: Cookie after setting: {cookie_after}")

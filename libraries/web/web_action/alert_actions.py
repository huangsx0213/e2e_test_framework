from .base import Base
import logging

class AlertActions(Base):
    def accept_alert(self):
        logging.info(f"{self.__class__.__name__}: Accepting alert")
        self.driver.switch_to.alert.accept()
        logging.info(f"{self.__class__.__name__}: Alert accepted successfully")

    def dismiss_alert(self):
        logging.info(f"{self.__class__.__name__}: Dismissing alert")
        self.driver.switch_to.alert.dismiss()
        logging.info(f"{self.__class__.__name__}: Alert dismissed successfully")

    def get_alert_text(self):
        logging.info(f"{self.__class__.__name__}: Getting alert text")
        alert_text = self.driver.switch_to.alert.text
        logging.info(f"{self.__class__.__name__}: Alert text retrieved: '{alert_text}'")
        return alert_text
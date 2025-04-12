import base64
import datetime
import io
import logging
import time
from PIL import Image
from robot.libraries.BuiltIn import BuiltIn
from .base import Base

class UtilsActions(Base):
    def capture_screenshot(self,description=None):
        try:
            if self.driver:
                screenshot_binary = self.driver.get_screenshot_as_png()
                image = Image.open(io.BytesIO(screenshot_binary))
                base_width = 1440
                w_percent = (base_width / float(image.size[0]))
                h_size = int((float(image.size[1]) * float(w_percent)))
                image = image.resize((base_width, h_size), Image.LANCZOS)
                buffer = io.BytesIO()
                image.save(buffer, format="WebP", quality=30)
                encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
                logging.info(
                    f"{self.__class__.__name__}: Screenshot captured successfully at: " + str(datetime.datetime.now())+ " with description: " + str(description))
                BuiltIn().log(f'<img src="data:image/webp;base64,{encoded_string}" width="1440px">', html=True)
            else:
                logging.error(f"{self.__class__.__name__}: WebDriver is not initialized.")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to capture screenshot: {str(e)}")
            BuiltIn().log(f"{self.__class__.__name__}: Failed to capture screenshot: {str(e)}", level="ERROR")

    def highlight_element(self, locator, duration=2, color="lightgreen", border="3px solid red", element_desc=None, condition="visibility"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Highlighting element [ {element_desc}:{locator} ] using JavaScript.")
        def apply_style(s):
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)
        original_style = element.get_attribute('style')
        for _ in range(int(duration)):
            apply_style(f"background: {color}; border: {border};")
            time.sleep(0.25)
            apply_style(original_style)
            time.sleep(0.25)
        logging.info(f"{self.__class__.__name__}: Highlighted element [ {element_desc}:{locator} ] using JavaScript successfully.")
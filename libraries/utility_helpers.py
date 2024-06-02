import os
import time
from functools import wraps
from lxml import etree


class UtilityHelpers:
    @staticmethod
    def get_file_format(file_path: str) -> str:
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower().strip('.')

    @staticmethod
    def format_xml(xml_string: str) -> str:
        parser = etree.XMLParser(remove_blank_text=True)
        xml_element = etree.fromstring(xml_string, parser)
        formatted_xml = etree.tostring(xml_element, pretty_print=False, encoding='unicode')
        return formatted_xml.strip()

    @staticmethod
    def time_calculation():
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                from libraries import logger
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                logger.log("INFO", f"Function '{func.__name__}' executed in {execution_time:.2f} seconds")
                return result

            return wrapper

        return decorator

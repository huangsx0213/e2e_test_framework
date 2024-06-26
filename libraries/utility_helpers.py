import json
import os
import time
from functools import wraps
from lxml import etree
from libraries.log_manager import logger_instance, logger
class UtilityHelpers:
    @staticmethod
    def get_file_format(file_path: str) -> str:
        """
        Determine the format of the file based on its extension.
        """
        if file_path.endswith('.json'):
            return 'json'
        elif file_path.endswith('.xml'):
            return 'xml'
        else:
            logger.error(f"Unsupported file format for file: {file_path}")
            raise ValueError("Unsupported file format")
    @staticmethod
    def escape_xml(value):
        """Escape XML characters."""
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    @staticmethod
    def format_json(data):
        """
        Formats a given dictionary as a pretty-printed JSON string.

        :param data: Dictionary to format.
        :return: Pretty-printed JSON string.
        """
        return json.dumps(data, indent=4)

    @staticmethod
    def format_xml(xml_string: str) -> str:
        """
        Formats a given XML string as a pretty-printed XML string without extra newlines.

        :param xml_string: XML string to format.
        :return: Pretty-printed XML string.
        """
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            xml_element = etree.fromstring(xml_string, parser)
            formatted_xml = etree.tostring(xml_element, pretty_print=True, encoding='unicode')
            return formatted_xml.strip()
        except Exception as e:
            raise ValueError(f"Invalid XML data: {str(e)}")
    @staticmethod
    def time_calculation():
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
                return result

            return wrapper

        return decorator

    @staticmethod
    def find_project_root(current_dir=os.getcwd()):
        while True:
            if os.path.exists(os.path.join(current_dir, '.project_root')):
                return current_dir
            parent = os.path.dirname(current_dir)
            if parent == current_dir:
                raise FileNotFoundError("Project root not found")
            current_dir = parent

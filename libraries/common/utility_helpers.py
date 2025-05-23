import json
import os
import time
from functools import wraps
from lxml import etree


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
            raise ValueError(f"UtilityHelpers: Unsupported file format for file: {file_path}")

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
            # check for XML declaration
            xml_declaration = ""
            if xml_string.startswith("<?xml"):
                declaration_end_index = xml_string.find("?>") + 2
                xml_declaration = xml_string[:declaration_end_index]
                xml_string = xml_string[declaration_end_index:].strip()

            parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False)
            xml_element = etree.fromstring(xml_string, parser)

            # Ensure CDATA sections are preserved
            def _preserve_cdata(element):
                if element.text and isinstance(element.text, etree.CDATA):
                    element.text = etree.CDATA(element.text)
                for child in element:
                    _preserve_cdata(child)
                    if child.tail and isinstance(child.tail, etree.CDATA):
                        child.tail = etree.CDATA(child.tail)

            _preserve_cdata(xml_element)
            formatted_xml = etree.tostring(xml_element, pretty_print=True, encoding='unicode')
            if xml_declaration:
                formatted_xml = xml_declaration + "\n" + formatted_xml
            return formatted_xml.strip()
        except Exception as e:
            raise ValueError(f"UtilityHelpers: Invalid XML data: {str(e)}")

    @staticmethod
    def time_calculation():
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                from libraries.common.log_manager import logger
                logger.info(f"UtilityHelpers: Function {func.__name__} executed in {execution_time:.4f} seconds")
                return result

            return wrapper

        return decorator

    @staticmethod
    def _find_project_root(current_dir=os.getcwd()):
        while True:
            if os.path.exists(os.path.join(current_dir, '.project_root')):
                return current_dir
            parent = os.path.dirname(current_dir)
            if parent == current_dir:
                raise FileNotFoundError("UtilityHelpers: Project root not found")
            current_dir = parent

    @staticmethod
    def get_project_root():
        # 尝试从脚本所在目录查找
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = UtilityHelpers._find_project_root(script_dir)

        if project_root is None:
            # 如果失败，尝试从当前工作目录查找
            current_dir = os.getcwd()
            project_root = UtilityHelpers._find_project_root(current_dir)

        if project_root is None:
            raise FileNotFoundError("UtilityHelpers: Project root not found")

        return project_root


PROJECT_ROOT = UtilityHelpers.get_project_root()

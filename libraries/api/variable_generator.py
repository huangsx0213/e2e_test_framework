import logging
import random
import string
import uuid
import datetime
from typing import Any, Dict, Callable


class VariableGenerator:
    @staticmethod
    def generate_dynamic_value(field_name: str) -> Any:
        handlers: Dict[str, Callable[[str], Any]] = {
            'uetr': VariableGenerator._generate_uuid4,
            'uuid4': VariableGenerator._generate_uuid4,
            'value_date': VariableGenerator._generate_current_day,
            'msg_id': VariableGenerator._generate_msg_id,
            'timestamp': VariableGenerator._generate_timestamp,
            'formated_timestamp': VariableGenerator._generate_formated_timestamp,
            'bic': VariableGenerator._generate_bic
        }
        return handlers.get(field_name, VariableGenerator._generate_default_value)()

    @staticmethod
    def _generate_uuid4() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def _generate_current_day(date_format: str = "%Y%m%d") -> str:
        return datetime.datetime.now().strftime(date_format)

    @staticmethod
    def _generate_msg_id() -> str:
        prefix = 'MSG'
        suffix = ''.join(random.choices(string.ascii_lowercase, k=5))
        timestamp = VariableGenerator._generate_timestamp()
        msg_id = f'{prefix}{timestamp}{suffix}'
        return msg_id

    @staticmethod
    def _generate_timestamp() -> str:
        return str(int(datetime.datetime.now().timestamp()))

    @staticmethod
    def _generate_formated_timestamp() -> str:
        now = datetime.datetime.now()
        timestamp_str = now.strftime("%m%d%H%M%S") + f"{now.microsecond // 1000:03d}"
        return timestamp_str

    @staticmethod
    def _generate_bic() -> str:
        return ''.join(random.choices(string.ascii_uppercase, k=8))

    @staticmethod
    def _generate_default_value() -> str:
        logging.error("VariableGenerator: No handler registered for this field.")
        return 'not support this dynamic field.'

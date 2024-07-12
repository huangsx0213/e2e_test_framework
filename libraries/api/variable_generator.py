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
            'value_date': VariableGenerator._generate_current_day,
            'msg_id': VariableGenerator._generate_msg_id,
            'timestamp': VariableGenerator._generate_timestamp,
            'age': VariableGenerator._generate_age,
            'address.street': VariableGenerator._generate_street,
            'phones.number': VariableGenerator._generate_phone_number,
            'address.zipcode': VariableGenerator._generate_zipcode,
            'token': VariableGenerator._generate_token,
            'test1': VariableGenerator._generate_test1,
            'test2': VariableGenerator._generate_test2,
        }

        return handlers.get(field_name, VariableGenerator._generate_default_value)()

    @staticmethod
    def _generate_uuid4() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def _generate_current_day(date_format: str = "%Y%m%d") -> str:
        current_date = datetime.datetime.now()
        return current_date.strftime(date_format)

    @staticmethod
    def _generate_msg_id() -> str:
        prefix = 'msg'
        suffix = ''.join(random.choices(string.ascii_lowercase, k=5))
        timestamp = VariableGenerator._generate_timestamp()
        msg_id = f'{prefix}{timestamp}{suffix}'
        return msg_id
    @staticmethod
    def _generate_timestamp() -> str:
        now = datetime.datetime.now()
        timestamp = now.strftime("%m%d%H%M%S") + str(now.microsecond)[:3]
        return timestamp
    @staticmethod
    def _generate_age() -> int:
        return 25

    @staticmethod
    def _generate_street() -> str:
        return 'Dynamic Street'

    @staticmethod
    def _generate_phone_number() -> str:
        return '5511539'

    @staticmethod
    def _generate_zipcode() -> str:
        return '00000'

    @staticmethod
    def _generate_token() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def _generate_test1() -> str:
        return 'Dynamic Test1'

    @staticmethod
    def _generate_test2() -> str:
        return 'Dynamic Test2'

    @staticmethod
    def _generate_default_value() -> str:
        return f'not support this dynamic field.'

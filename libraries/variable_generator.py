import uuid
from typing import Any, Dict, Callable


class VariableGenerator:
    @staticmethod
    def generate_dynamic_value(field_name: str, saved_fields: Dict[str, Any] = None) -> Any:
        if saved_fields and field_name in saved_fields:
            return saved_fields[field_name]

        handlers: Dict[str, Callable[[str], Any]] = {
            'user_id': VariableGenerator._generate_user_id,
            'name': VariableGenerator._generate_name,
            'email': VariableGenerator._generate_email,
            'age': VariableGenerator._generate_age,
            'address.street': VariableGenerator._generate_street,
            'phones.number': VariableGenerator._generate_phone_number,
            'address.zipcode': VariableGenerator._generate_zipcode,
            'token': VariableGenerator._generate_token,
            'test1': VariableGenerator._generate_test1,
            'test2': VariableGenerator._generate_test2,
        }

        return handlers.get(field_name, VariableGenerator._generate_default_value)(field_name)

    @staticmethod
    def _generate_user_id(field_name: str = None) -> int:
        return 1  # Example value, actual implementation can vary

    @staticmethod
    def _generate_name(field_name: str = None) -> str:
        return 'Dynamic Name'

    @staticmethod
    def _generate_email(field_name: str = None) -> str:
        return 'dynamic@example.com'

    @staticmethod
    def _generate_age(field_name: str = None) -> int:
        return 25

    @staticmethod
    def _generate_street(field_name: str = None) -> str:
        return 'Dynamic Street'

    @staticmethod
    def _generate_phone_number(field_name: str = None) -> str:
        return '5511539'

    @staticmethod
    def _generate_zipcode(field_name: str = None) -> str:
        return '00000'

    @staticmethod
    def _generate_token(field_name: str = None) -> str:
        return str(uuid.uuid4())

    @staticmethod
    def _generate_test1(field_name: str = None) -> str:
        return 'Dynamic Test1'

    @staticmethod
    def _generate_test2(field_name: str = None) -> str:
        return 'Dynamic Test2'

    @staticmethod
    def _generate_default_value(field_name: str) -> str:
        return f'dynamic_{field_name}'

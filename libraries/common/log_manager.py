import logging
import logging.config
import os
import yaml
from libraries.common.utility_helpers import PROJECT_ROOT


class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path=None):
        if not hasattr(self, 'initialized'):
            self.config_path = config_path or os.path.join(PROJECT_ROOT, 'configs', 'logging_config.yaml')
            self.log_file_name = "robot_testing"
            self.load_config()
            self.initialized = True

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)

            log_file_path = os.path.join(PROJECT_ROOT, 'reports', f"{self.log_file_name}.log")
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

            if 'file' in config['handlers']:
                config['handlers']['file']['filename'] = log_file_path

            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=logging.DEBUG)

        self.logger = logging.getLogger('e2e_testing')

    def get_logger(self):
        return self.logger


class ColorLogger:
    @staticmethod
    def success(message):
        return f'<span style="background-color: #90EE90; padding: 2px 5px; border-radius: 3px;">{message}</span>'

    @staticmethod
    def error(message):
        return f'<span style="background-color: #FFB6C1; padding: 2px 5px; border-radius: 3px;">{message}</span>'

    @staticmethod
    def info(message):
        return f'<span style="background-color: #B8E2F2; padding: 2px 5px; border-radius: 3px;">{message}</span>'

logger_instance = Logger()
logger = logger_instance.get_logger()

__all__ = ['logger', 'logger_instance', 'ColorLogger']

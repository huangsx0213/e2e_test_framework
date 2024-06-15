import logging
import logging.config
import yaml
import os
from datetime import datetime


class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path='configs/logging_config.yaml'):
        if not hasattr(self, 'initialized'):
            self.config_path = config_path
            self.logger = None
            self.load_config()
            self.initialized = True

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)

                # Generate dynamic log file name with timestamp
                log_file_name = f"logs/e2e_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

                # Ensure the directory for the log file exists
                log_dir = os.path.dirname(log_file_name)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)

                # Update the log file name in the configuration
                config['handlers']['file']['filename'] = log_file_name

                logging.config.dictConfig(config)
                self.logger = logging.getLogger('e2e_testing')
        else:
            logging.basicConfig(level=logging.DEBUG)
            self.logger = logging.getLogger('e2e_testing')

    def get_logger(self):
        return self.logger



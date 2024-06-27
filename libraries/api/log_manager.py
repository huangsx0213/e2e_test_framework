import logging
import logging.config
import os
import re
import yaml
import uuid
from datetime import datetime
from libraries.api.utility_helpers import PROJECT_ROOT


class HTMLLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.html_log_entries = {}

    def emit(self, record):
        msg = record.getMessage()
        match = re.match(r'\[TSID:(.*?)\]\s*(.*)', msg, re.DOTALL)
        if match:
            ts_id = match.group(1)
            message = match.group(2)
        else:
            ts_id = 'default_tsid'
            message = msg

        log_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': message
        }
        self.html_log_entries.setdefault(ts_id, []).append(log_entry)


class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path=None):
        self.project_root: str = PROJECT_ROOT

        if not hasattr(self, 'initialized'):
            self.config_path: str = config_path or os.path.join(self.project_root, 'configs', 'logging_config.yaml')
            self.log_file_name = ''
            self.logger = None
            self.load_config()
            self.initialized = True

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                self.log_file_name = f"e2e_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                # Generate dynamic log file name with timestamp
                log_file_name = os.path.join(self.project_root, 'logs', f"{self.log_file_name}.log")

                # Ensure the directory for the log file exists
                log_dir = os.path.dirname(log_file_name)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)

                # Update the log file name in the configuration
                config['handlers']['file']['filename'] = log_file_name

                logging.config.dictConfig(config)
                self.logger = logging.getLogger('e2e_testing')

                # Add custom HTML report log handler
                self.html_handler = HTMLLogHandler()
                self.logger.addHandler(self.html_handler)
        else:
            logging.basicConfig(level=logging.DEBUG)
            self.logger = logging.getLogger('e2e_testing')

    def get_logger(self):
        return self.logger

    def get_html_log_entries(self):
        return self.html_handler.html_log_entries


# 创建并配置 logger 实例
logger_instance = Logger()
logger = logger_instance.get_logger()

# 导出 logger
__all__ = ['logger', 'logger_instance']

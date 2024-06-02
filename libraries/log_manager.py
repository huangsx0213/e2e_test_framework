import json
import os
import time
from datetime import datetime
from typing import Dict, Union
import requests
from libraries.utility_helpers import UtilityHelpers

class Logger:
    _instance = None
    _log_levels = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_dir: str = 'log', log_level: str = 'INFO') -> None:
        if not hasattr(self, 'initialized'):
            self.log_dir: str = log_dir
            self.log_filename: str = self.generate_log_filename()
            self.log_filepath: str = os.path.join(self.log_dir, self.log_filename)
            self.log_level: int = self._log_levels.get(log_level.upper(), 10)
            self.ensure_log_dir_exists()
            self.initialized = True

    def set_level(self, level: str) -> None:
        self.log_level = self._log_levels.get(level.upper(), 10)

    def generate_log_filename(self) -> str:
        timestamp = int(time.time())
        date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d_%H-%M-%S')
        return f"log_{date_str}.log"

    def ensure_log_dir_exists(self) -> None:
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
        except OSError as e:
            raise RuntimeError(f"Failed to create log directory {self.log_dir}: {str(e)}")

    def log(self, level: str, message: str) -> None:
        if self._log_levels.get(level.upper(), 0) >= self.log_level:
            try:
                timestamp = int(time.time())
                date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d_%H-%M-%S')
                log_content = f"{date_str} [{level.upper()}]: {message}"

                # Write to log file
                with open(self.log_filepath, 'a') as log_file:
                    log_file.write(log_content + "\n")

                # Print to console
                print(log_content)

            except (OSError, IOError) as e:
                raise ValueError(f"Failed to write log message: {str(e)}")

    def log_request(self, ts_id, endpoint_name, method, endpoint: str, headers: Dict[str, str],
                    body: Union[Dict, str], format_type: str) -> None:
        if self._log_levels.get('DEBUG', 0) >= self.log_level:
            try:
                timestamp = int(time.time())
                date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d_%H-%M-%S')
                if format_type == 'json':
                    formatted_body = body
                elif format_type == 'xml':
                    formatted_body = UtilityHelpers.format_xml(body)
                log_content1 = {
                    "method": method,
                    "endpoint": endpoint,
                    "headers": headers,
                    "body": formatted_body,
                    "format_type": format_type
                }
                log_content2 = f"{date_str} [DEBUG] [Test step ID: {ts_id}] [Endpoint: {endpoint_name}]: Request:"

                with open(self.log_filepath, 'a') as log_file:
                    log_file.write(log_content2 + "\n")
                    json.dump(log_content1, log_file, indent=4)
                    log_file.write("\n")

                # Print request log to console
                print(log_content2)
                print(json.dumps(log_content1, indent=4))

            except (OSError, IOError) as e:
                raise ValueError(f"Failed to log request: {str(e)}")

    def log_response(self, ts_id, endpoint_name: str, response: requests.Response, format_type: str) -> None:
        if self._log_levels.get('DEBUG', 0) >= self.log_level:
            try:
                timestamp = int(time.time())
                date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d_%H-%M-%S')
                log_content1 = {
                    "response_status_code": response.status_code,
                    "response_headers": dict(response.headers),
                    "response_body": json.loads(response.text) if format_type == 'json' else response.text
                }
                log_content2 = f"{date_str} [DEBUG] [Test step ID: {ts_id}] [Endpoint: {endpoint_name}]: Response:"

                with open(self.log_filepath, 'a') as log_file:
                    log_file.write(log_content2 + "\n")
                    json.dump(log_content1, log_file, indent=4)
                    log_file.write("\n")

                # Print response log to console
                print(log_content2)
                print(json.dumps(log_content1, indent=4))

            except (OSError, IOError) as e:
                raise ValueError(f"Failed to log response: {str(e)}")
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Failed to log response(failed to decode response body): {str(e)}.\n Response body:\n{response.text}")
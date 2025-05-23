import requests
import urllib3
from typing import Dict, Union, Optional
import time
import logging


class RequestSender:
    @staticmethod
    def send_request(url: str, method: str, headers: Optional[Dict[str, str]] = None,
                     body: Optional[Union[Dict, str]] = None, format_type: str = 'json') -> (requests.Response, float, Optional[str]):
        requests_method = RequestSender._get_request_method(method)
        start_time = time.time()
        urllib3.disable_warnings()
        try:
            if format_type == 'json':
                response = requests_method(url, headers=headers, json=body, verify=False)
            elif format_type == 'xml':
                if headers is not None:
                    headers['Content-Type'] = 'application/xml'
                response = requests_method(url, headers=headers, data=body, verify=False)
            else:
                logging.error(f"Unsupported format type: {format_type}")
                raise ValueError(f"RequestSender: Unsupported format type: {format_type}")
            response.raise_for_status()
        except requests.exceptions.SSLError as e:
            logging.error(f"SSL verification failed: {str(e)}")
            raise
        except requests.RequestException as e:
            logging.error(f"Sending request error: {str(e)}")
            raise
        except ValueError as e:
            logging.error(str(e))
            raise

        execution_time = time.time() - start_time
        return response, execution_time

    @staticmethod
    def _get_request_method(method: str):
        methods = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'DELETE': requests.delete,
            'PATCH': requests.patch
        }

        if method in methods:
            return methods[method]
        else:
            logging.warning(f"Unsupported HTTP method: {method}")
            return methods['GET']  # 返回默认方法 GET

import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from libraries import logger


class HTMLReportGenerator:
    def __init__(self):
        #self.html_log_entries = logger_instance.get_html_log_entries()
        self.ensure_log_dir_exists()

    def ensure_log_dir_exists(self, log_dir='output') -> None:
        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
        except OSError as e:
            logger.error(f"Failed to create log directory {log_dir}: {str(e)}")
            raise

    def generate_html_report(self, pending_operations, report_path=None):
        try:
            env = Environment(loader=FileSystemLoader('configs/report_template'))
            template = env.get_template('report_template.html')

            results = []
            for operation in pending_operations:
                test_step = operation['test_step']
                log_entries = self.html_log_entries.get(test_step['TSID'], [])

                formatted_logs = [{
                    'log_id': log['id'],
                    'timestamp': log['timestamp'],
                    'level': log['level'],
                    'message': log['message'],
                    'details': log['details'],
                    'result': log['result']
                } for log in log_entries]

                results.append({
                    'tcid': test_step['TCID'],
                    'tsid': test_step['TSID'],
                    'endpoint': test_step['Endpoint'],
                    'status': operation['actual_status'],
                    'result': operation['overall_result'],
                    'expected_result': test_step['Exp Result'],
                    'actual_result': operation['formatted_results'],
                    'saved_fields': operation['formatted_fields_saved'],
                    'execution_time': f"{operation['execution_time']:.2f}s",
                    'logs': formatted_logs
                })
            # Use the start time from the logger to generate the report filename
            if report_path is None:
                start_time = datetime.fromtimestamp(logger.start_time).strftime('%Y-%m-%d_%H-%M-%S')
                report_path = f"output/report_{start_time}.html"
            html_content = template.render(results=results)
            with open(report_path, 'w') as report_file:
                report_file.write(html_content)
            logger.info(f"HTML report generated at: {report_path}")
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {str(e)}")
            raise

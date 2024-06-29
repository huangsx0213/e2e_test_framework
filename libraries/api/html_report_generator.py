import os
from jinja2 import Environment, FileSystemLoader
from libraries.common.log_manager import logger_instance
from libraries.api.utility_helpers import UtilityHelpers, PROJECT_ROOT


class HTMLReportGenerator:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.ensure_log_dir_exists()
        self.html_log_entries = {}
        self.report_file_name = ''

    def ensure_log_dir_exists(self, log_dir=None) -> None:
        log_dir = log_dir or os.path.join(self.project_root, 'output')
        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
        except OSError as e:
            raise ValueError(f"Failed to create log directory {log_dir}: {str(e)}")

    def generate_html_report(self, pending_operations, report_path=None):
        try:
            env = Environment(loader=FileSystemLoader(os.path.join(self.project_root, 'configs', 'report_template')))
            env.filters['escape_xml'] = UtilityHelpers.escape_xml
            template = env.get_template('report_template.html')
            self.html_log_entries = logger_instance.get_html_log_entries()
            self.report_file_name = logger_instance.log_file_name
            results = []
            for operation in pending_operations:
                test_step = operation['test_step']
                log_entries = self.html_log_entries.get(test_step['TSID'], [])

                formatted_logs = [{
                    'log_id': log['id'],
                    'timestamp': log['timestamp'],
                    'level': log['level'],
                    'message': log['message']
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

            if report_path is None:
                report_path = os.path.join(self.project_root, 'output', f'{self.report_file_name}.html')
            html_content = template.render(results=results)
            with open(report_path, 'w') as report_file:
                report_file.write(html_content)
        except Exception as e:
            raise ValueError(f"Failed to generate HTML report: {str(e)}")

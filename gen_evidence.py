import os
import re
import base64
import shutil
from robot.api import ExecutionResult, ResultVisitor
from docx import Document
from docx.shared import Inches, RGBColor
from datetime import datetime
import io
from PIL import Image
from libraries.common.utility_helpers import PROJECT_ROOT


# Define ScreenshotCollector class to collect test results and screenshots
class ScreenshotCollector(ResultVisitor):
    def __init__(self):
        self.test_results = []  # Store all test case results
        self.current_test = None  # Current test case
        self.base64_screenshots = []  # Screenshots for current test case
        self.current_keyword = None  # Current keyword (step)
        self.last_action_step = None  # Last action step

    def start_test(self, test):
        # Initialize current test case information
        self.current_test = {
            'id': test.id,
            'name': test.name,
            'doc': test.doc,
            'status': test.status,
            'suites': self._get_parent_suites(test),
            'steps': [],
            'base64_screenshots': [],
            'start_time': test.starttime,
            'end_time': test.endtime,
            'duration': test.elapsedtime
        }
        self.base64_screenshots = []

    def end_test(self, test):
        # Add current test case to results, regardless of screenshots
        self.current_test['base64_screenshots'] = self.base64_screenshots
        self.test_results.append(self.current_test)
        self.current_test = None
        self.current_keyword = None

    def start_keyword(self, keyword):
        if self.current_test is None:
            return

        # Collect test step information
        step_info = {
            'name': keyword.name,
            'status': keyword.status,
            'messages': []
        }
        self.current_keyword = step_info

        for msg in keyword.messages:
            if "Executing action" in msg.message:
                step_info['messages'].append(msg.message)
                if "RobotTestExecutor: Executing action" in msg.message:
                    self.last_action_step = {
                        'name': self.current_keyword['name'],
                        'message': msg.message
                    }

            # Handle base64 encoded screenshots
            if msg.html and "img src=" in msg.message:
                base64_match = re.search(r'img src="data:image/[^;]+;base64,([^"]+)"', msg.message)
                if base64_match:
                    screenshot_info = {
                        'data': base64_match.group(1),
                        'step': self.last_action_step if self.last_action_step else {'name': self.current_keyword['name']}
                    }
                    self.base64_screenshots.append(screenshot_info)

        if step_info['messages']:
            self.current_test['steps'].append(step_info)

    def _get_parent_suites(self, test):
        # Get parent suite paths for the test case
        suites = []
        current = test.parent
        while current is not None and hasattr(current, 'name'):
            suites.append({'id': current.id, 'name': current.name, 'doc': current.doc})
            current = getattr(current, 'parent', None)
        suites.reverse()
        return suites

# Parse Robot Framework output file
def parse_robot_output(xml_path):
    result = ExecutionResult(xml_path)
    collector = ScreenshotCollector()
    result.visit(collector)
    print(f"Found {len(collector.test_results)} test cases")
    return collector.test_results

# Define WordReportGenerator class to generate Word report
class WordReportGenerator:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or PROJECT_ROOT
        self.temp_dir = None  # Temporary screenshot directory

    def format_action_message(self, message):
        # Format action message for better readability
        if not message or "RobotTestExecutor: Executing action" not in message:
            return message
        try:
            action_match = re.search(r'action:\[([^\]]+)\]', message)
            page_match = re.search(r'page:\[([^\]]+)\]', message)
            module_match = re.search(r'module:\[([^\]]+)\]', message)
            element_match = re.search(r'element:\[([^\]]+)\]', message)
            params_match = re.search(r'with parameters:\[(.+?)\](?:\s|$)', message)

            action = action_match.group(1) if action_match else 'Unknown Action'
            page = page_match.group(1) if page_match else 'Unknown Page'
            module = module_match.group(1) if module_match else 'Unknown Module'
            element = element_match.group(1) if element_match else None
            params = params_match.group(1) if params_match else None

            base_msg = f'Execute [{action}] in [{page}] page [{module}] module'
            if element:
                base_msg= f'{base_msg}, target element: [{element}]'
            if params:
                base_msg= f'{base_msg}, parameters: [{params}]'
            return base_msg
        except Exception as e:
            print(f"Error formatting message: {str(e)}")
            return message

    def process_base64_image(self, base64_data):
        # Process base64 encoded image data
        if isinstance(base64_data, dict) and 'data' in base64_data:
            base64_data = base64_data['data']
        try:
            image_data = base64.b64decode(base64_data)
            return Image.open(io.BytesIO(image_data))
        except Exception as e:
            print(f"Failed to decode base64 data directly: {str(e)}")
            try:
                cleaned_data = base64_data.replace(" ", "").replace("\n", "")
                padding = 4 - (len(cleaned_data) % 4) if len(cleaned_data) % 4 != 0 else 0
                cleaned_data += "=" * padding
                image_data = base64.b64decode(cleaned_data)
                return Image.open(io.BytesIO(image_data))
            except Exception as e2:
                print(f"Failed to decode base64 data after cleaning: {str(e2)}")
                return None

    def save_image_for_word(self, img, output_dir, index, test_name):
        # Save image in Word compatible format
        try:
            os.makedirs(output_dir, exist_ok=True)
            safe_test_name = re.sub(r'[\\/*?:"<>|]', "_", test_name)
            filename = f"{safe_test_name}_{index}.jpg"
            filepath = os.path.join(output_dir, filename)

            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                rgb_img.save(filepath, 'JPEG', quality=95)
            else:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(filepath, 'JPEG', quality=95)
            print(f"Screenshot saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving image: {str(e)}")
            return None

    def generate_report(self, xml_path=None, output_file=None):
        # Generate Word report
        xml_path = xml_path or os.path.join(self.base_dir, 'reports', 'output.xml')
        output_file = output_file or os.path.join(self.base_dir, 'reports', 'test_evidence_report.docx')

        self.temp_dir = os.path.join(os.path.dirname(output_file), 'temp_screenshots')
        os.makedirs(self.temp_dir, exist_ok=True)
        print(f"Created temporary screenshot directory: {self.temp_dir}")

        print(f'Parsing Robot Framework output file: {xml_path}')
        test_results = parse_robot_output(xml_path)

        if not test_results:
            print('No test cases found')
            return None

        return self._generate_word_report(test_results, output_file)

    def _generate_word_report(self, test_results, output_file):
        # Internal method: Generate Word report
        doc = Document()

        # Set document properties
        doc.core_properties.title = 'Robot Framework Test Evidence'
        doc.core_properties.author = 'end to end testing'  # Replace with actual author
        doc.core_properties.created = datetime.now()

        # Add title and generation time
        doc.add_heading('Robot Framework Test Evidence', 0)
        doc.add_paragraph(f'Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        # Add test summary
        total_tests = len(test_results)
        passed = sum(1 for test in test_results if test['status'] == 'PASS')
        failed = total_tests - passed
        doc.add_heading('Test Summary', level=1)
        doc.add_paragraph(f'Total Test Cases: {total_tests}')
        doc.add_paragraph(f'Passed: {passed}')
        doc.add_paragraph(f'Failed: {failed}')

        # Add list of failed test cases
        if failed > 0:
            doc.add_heading('Failed Test Cases', level=2)
            for test in test_results:
                if test['status'] == 'FAIL':
                    suite_path = ' > '.join([suite['name'] for suite in test['suites']])
                    doc.add_paragraph(f'{test["name"]} - {suite_path}')

        # Add each test case
        for i, test in enumerate(test_results):
            if i > 0:
                doc.add_page_break()  # New page for each test case

            doc.add_heading(f'Test Case: {test["name"]}', 1)
            suite_path = ' > '.join([suite['name'] for suite in test['suites']])
            doc.add_paragraph(f'Test Suite Path: {suite_path}')

            # Test result
            status_text = 'Pass' if test['status'] == 'PASS' else 'Fail'
            p = doc.add_paragraph('Test Result: ')
            run = p.add_run(status_text)
            run.bold = True
            run.font.color.rgb = RGBColor(0, 128, 0) if test['status'] == 'PASS' else RGBColor(255, 0, 0)

            # Time information
            if 'start_time' in test:
                doc.add_paragraph(f'Start Time: {test["start_time"]}')
            if 'end_time' in test:
                doc.add_paragraph(f'End Time: {test["end_time"]}')
            if 'duration' in test:
                doc.add_paragraph(f'Duration: {test["duration"]}')

            # Test description
            if test['doc']:
                doc.add_heading('Test Description', 2)
                doc.add_paragraph(test['doc'])

            # Test suite description
            for suite in test['suites']:
                if suite['doc']:
                    doc.add_heading(f'Test Suite "{suite["name"]}" Description', 2)
                    doc.add_paragraph(suite['doc'])

            # Test steps
            if test['steps']:
                doc.add_heading('Test Steps', 2)
                for step_num, step in enumerate(test['steps'], 1):
                    p = doc.add_paragraph()
                    p.add_run(f'Step {step_num}: {step["name"]} - {step["status"]}').bold = True
                    for msg in step['messages']:
                        formatted_msg = self.format_action_message(msg)
                        doc.add_paragraph(f'- {formatted_msg}', style='List Bullet')

            # Handle screenshots
            if test['base64_screenshots']:
                doc.add_heading('Test Screenshots', 2)
                for screenshot_num, screenshot_info in enumerate(test['base64_screenshots'], 1):
                    base64_data = screenshot_info['data']
                    step_info = screenshot_info.get('step', {})
                    if step_info and 'name' in step_info:
                        p = doc.add_paragraph()
                        p.add_run(f'Screenshot {screenshot_num} for step:').bold = True
                        if 'message' in step_info and "RobotTestExecutor: Executing action" in step_info['message']:
                            formatted_msg = self.format_action_message(step_info['message'])
                            doc.add_paragraph(f'Action: {formatted_msg}')
                    else:
                        doc.add_paragraph(f'Screenshot {screenshot_num}: (No associated step)')

                    img = self.process_base64_image(base64_data)
                    if img:
                        img_file = self.save_image_for_word(img, self.temp_dir, screenshot_num, test['name'])
                        if img_file and os.path.exists(img_file):
                            try:
                                doc.add_picture(img_file, width=Inches(6))
                                print(f"Successfully added image {img_file} to document")
                            except Exception as e:
                                print(f"Failed to add image to document: {str(e)}")
                                doc.add_paragraph(f'Cannot add screenshot: {str(e)}')
                    else:
                        doc.add_paragraph('Failed to parse base64 screenshot data')
            else:
                doc.add_paragraph('No screenshots found')

            doc.add_paragraph('_' * 50)  # Separator line

        # Save document
        try:
            doc.save(output_file)
            print(f'Report generated: {output_file}')
        except Exception as e:
            print(f'Error saving report: {str(e)}')
            return None

        # Cleanup temporary directory
        self._cleanup_temp_dir()
        return output_file

    def _cleanup_temp_dir(self):
        # Cleanup temporary screenshot directory
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned temporary screenshot directory: {self.temp_dir}")
        except Exception as e:
            print(f"Failed to clean temporary screenshot directory: {str(e)}")

# Main function
def main():
    generator = WordReportGenerator()
    generator.generate_report()

if __name__ == "__main__":
    main()

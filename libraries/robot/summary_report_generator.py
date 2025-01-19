import codecs
import logging
import os
from typing import Dict, List, Any
from jinja2 import FileSystemLoader, Environment, TemplateNotFound
from pandas import DataFrame
from robot.api import ExecutionResult
from libraries.common.utility_helpers import PROJECT_ROOT
import re


class SummaryReportGenerator:
    def __init__(self, output_xml_path: str):
        self.output_xml_path = output_xml_path
        self.templates_dir = os.path.join(PROJECT_ROOT, 'templates')
        self.test_results = self._parse_robot_output()

    def _parse_robot_output(self) -> List[Dict]:
        """Parses the robot output.xml and extracts test results."""
        try:
            result = ExecutionResult(self.output_xml_path)
            all_results = []

            for test in result.suite.tests:
                test_results = self._extract_results_from_test(test)
                all_results.extend(test_results)

            return all_results

        except Exception as e:
            logging.error(f"HTMLReportGenerator: Error parsing Robot output.xml: {e}")
            return []

    def _extract_results_from_test(self, test) -> List[Dict]:
        """Extracts all test results from a robot test case."""
        test_results = []
        for keyword in test.body:
            if keyword.name == 'Execute Api Test Case':
                test_case_id = keyword.args[0]

                for log_msg in keyword.messages:
                     if "Main Test=> ResponseValidator: Asserting" in log_msg.message:
                        test_results.append(self._parse_assertion_log(log_msg.message, test_case_id, test.doc))

                     elif "Main Test=> ResponseValidator: Dynamic check" in log_msg.message:
                         test_results.append(self._parse_dynamic_check_log(log_msg.message, test_case_id, test.doc))

                     elif "Main Test=> ResponseValidator: Postcheck" in log_msg.message:
                          test_results.append(
                              self._parse_pre_post_check_log(log_msg.message, "Postcheck", test_case_id, test.doc))

                     elif "Main Test=> ResponseValidator: Precheck" in log_msg.message:
                         test_results.append(
                             self._parse_pre_post_check_log(log_msg.message, "Precheck", test_case_id, test.doc))
                     elif "Main Test=> ResponseValidator: Database validation" in log_msg.message:
                         test_results.append(self._parse_database_validation_log(log_msg.message, test_case_id, test.doc))
        return test_results


    def _parse_assertion_log(self, log_message, tcid, description):
        parts = re.split(r"Main Test=> ResponseValidator: Asserting:\s*(.*?),\s*Expected:\s*(.*?),\s*Actual:\s*([^<]*)", log_message,
                         flags=re.DOTALL | re.MULTILINE)
        if len(parts) != 5:
            logging.error(f"Could not parse assertion log message: {log_message}")
            return {}

        field, expected, actual = parts[1].strip(), parts[2].strip(), parts[3].strip()

        return {
             "TCID": tcid,
             "Description": description,
             "Type": "Assertions",
             "Field": field,
             "Pre Value": '',
             "Post Value": '',
             "Expected": expected.strip(),
             "Actual": actual.strip(),
             "Result": "Pass" if actual.strip() == expected.strip() else "Fail",
         }

    def _parse_dynamic_check_log(self, log_message, tcid, description):
        parts = re.split(
            r"Main Test=> ResponseValidator: Dynamic check for\s*(.*?)\.\s*(?:Pre Value:\s*(.*?),\s*Post Value:\s*(.*?),\s*)?Expected diff:\s*([^<]*?),\s*Actual diff:\s*([^<]*)",
            log_message, flags=re.DOTALL | re.MULTILINE)
        if len(parts) != 7:
            logging.error(f"Could not parse dynamic check log message: {log_message}")
            return {}

        field, pre_value, post_value, expected_diff_str, actual_diff_str = parts[1].strip(), parts[2].strip() if parts[2] else None, parts[3].strip() if parts[3] else None, parts[
            4].strip(), parts[5].strip()
        actual_diff = float(actual_diff_str)
        expected_diff = float(expected_diff_str)

        return {
            "TCID": tcid,
            "Description": description,
            "Type": "Dynamic Checks",
            "Field": field,
            "Pre Value": pre_value if pre_value else '',
            "Post Value": post_value if post_value else '',
            "Actual Diff": actual_diff_str,
            "Expected Diff": expected_diff_str,
            "Result": "Pass" if actual_diff == expected_diff else "Fail",
        }

    def _parse_pre_post_check_log(self, log_message, check_type, tcid, description):
        parts = re.split(rf"Main Test=> ResponseValidator: {check_type} for\s*(.*?)\s*- Expected value:\s*([^<]*?),\s*Actual value:\s*([^<]*)", log_message, flags=re.DOTALL | re.MULTILINE)
        if len(parts) != 5:
            logging.error(f"Could not parse pre/post check log message: {log_message}")
            return {}

        field, expected_value, actual_value = parts[1].strip(), parts[2].strip(), parts[3].strip()

        return {
            "TCID": tcid,
             "Description": description,
            "Type": f"{check_type} Checks",
            "Field": field,
            "Pre Value": '',
            "Post Value": '',
            "Expected": expected_value.strip(),
            "Actual": actual_value.strip(),
            "Result": "Pass" if actual_value.strip() == expected_value.strip() else "Fail",
        }

    def _parse_database_validation_log(self, log_message, tcid, description):
        """Parses the database validation log message."""
        parts = re.split(
            r"Main Test=> ResponseValidator: Database validation for '([^']*)' in table '([^']*)'\. Expected: '([^']*)', Actual: '([^']*)'\.",
            log_message, flags=re.DOTALL | re.MULTILINE
        )

        if len(parts) != 6:
            logging.error(f"Could not parse database validation log message: {log_message}")
            return {}

        field, table_name, expected_value, actual_value = parts[1].strip(), parts[2].strip(), parts[3].strip(), parts[4].strip()

        return {
            "TCID": tcid,
            "Description": description,
            "Type": "Database Checks",
            "Field": f"{table_name}.{field}",  # added table name to the field
            "Pre Value": '',
            "Post Value": '',
            "Expected": expected_value,
            "Actual": actual_value,
            "Result": "Pass" if actual_value == expected_value else "Fail",
        }
    def generate_html_report(self) -> str:
        """
        Generates the HTML report content.
        """
        try:
            file_loader = FileSystemLoader(self.templates_dir)
            env = Environment(loader=file_loader)
            template = env.get_template('test_summary_template.html')

            flattened_data = self._flatten_results(self.test_results)
            if not flattened_data:  # Check if flattened_data is empty
                return "No test results to display."

            df = DataFrame(flattened_data)

            # Reorder columns if needed
            df = df[
                [
                    "TCID",
                    "Description",
                    "Type",
                    "Field",
                    "Pre Value",
                    "Post Value",
                    "Expected",
                    "Actual",
                    "Result",
                ]
            ]

            # Create the HTML table with merged cells and color-coded results
            html_table = self._create_html_table(df)
            html_content = template.render(html_table=html_table)

             # Save the HTML report to a file
            report_file = os.path.join(PROJECT_ROOT, "report", "test_summary.html")
            os.makedirs(os.path.dirname(report_file), exist_ok=True)  # Ensure the directory exists
            with codecs.open(report_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.info(f"HTMLReportGenerator: Test report saved to: {report_file}")

        except TemplateNotFound as e:
            logging.error(f"HTMLReportGenerator: Template not found: {e}")
            raise
        except Exception as e:
            logging.error(f"HTMLReportGenerator: Error generating HTML report: {e}")
            raise

    def _flatten_results(self, test_results: List[Dict]):
        """
        Flattens the test results data.
        """
        for result in test_results:
            row = {
                "TCID": result["TCID"],
                "Description": result["Description"],
                "Type": result["Type"],
                "Field": result["Field"],
                "Pre Value": result.get("Pre Value", ""),
                "Post Value": result.get("Post Value", ""),
                "Expected": result.get("Expected Diff", "") if result.get("Expected Diff") else result.get("Expected", ""),
                "Actual": result.get("Actual Diff", "") if result.get("Actual Diff") else result.get("Actual", ""),
                "Result": result["Result"]
            }
            yield row

    def _create_html_table(self, df: DataFrame) -> str:
        """
        Creates the HTML table content.
        """
        html_table = '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">\n'

        # Add table headers
        html_table += '<tr>\n'
        for col in df.columns:
            html_table += f'<th style="background-color: #f2f2f2; text-align: center;">{col}</th>\n'
        html_table += '</tr>\n'

        # Add table rows
        current_tcid = None
        current_description = None
        tcid_rowspan = 1
        description_rowspan = 1
        for i, row in df.iterrows():
            if row["TCID"] == current_tcid and row["Description"] == current_description:
                tcid_rowspan += 1
                description_rowspan += 1
                html_table += '<tr>\n'
                for col in df.columns[2:]:  # Skip TCID and Description columns
                    if col == "Result":
                        color = "green" if row[col].upper() == "PASS" else ("red" if row[col].upper() == "FAIL" else "orange")
                        # Use font color instead of background color
                        html_table += f'<td style="text-align: center; color: {color};">{row[col]}</td>\n'
                    else:
                        html_table += f'<td style="text-align: center;">{row[col]}</td>\n'
                html_table += '</tr>\n'
            else:
                if current_tcid is not None:
                    # Update the rowspan for the previous TCID and Description groups
                    html_table = html_table.replace(
                        f'<td rowspan="placeholder_tcid">{current_tcid}</td>',
                        f'<td rowspan="{tcid_rowspan}" style="text-align: center; vertical-align: middle;">{current_tcid}</td>',
                        1
                    )
                    html_table = html_table.replace(
                        f'<td rowspan="placeholder_description">{current_description}</td>',
                        f'<td rowspan="{description_rowspan}" style="text-align: center; vertical-align: middle;">{current_description}</td>',
                        1
                    )
                current_tcid = row["TCID"]
                current_description = row["Description"]
                tcid_rowspan = 1
                description_rowspan = 1
                html_table += '<tr>\n'
                html_table += f'<td rowspan="placeholder_tcid">{row["TCID"]}</td>\n'  # Placeholder for TCID rowspan
                html_table += f'<td rowspan="placeholder_description">{row["Description"]}</td>\n'  # Placeholder for Description rowspan
                for col in df.columns[2:]:  # Skip TCID and Description columns
                    if col == "Result":
                        color = "green" if row[col].upper() == "PASS" else ("red" if row[col].upper() == "FAIL" else "orange")
                        # Use font color instead of background color
                        html_table += f'<td style="text-align: center; color: {color};">{row[col]}</td>\n'
                    else:
                        html_table += f'<td style="text-align: center;">{row[col]}</td>\n'
                html_table += '</tr>\n'

        # Update the rowspan for the last TCID and Description groups
        if current_tcid is not None:
            html_table = html_table.replace(
                f'<td rowspan="placeholder_tcid">{current_tcid}</td>',
                f'<td rowspan="{tcid_rowspan}" style="text-align: center; vertical-align: middle;">{current_tcid}</td>',
                1
            )
            html_table = html_table.replace(
                f'<td rowspan="placeholder_description">{current_description}</td>',
                f'<td rowspan="{description_rowspan}" style="text-align: center; vertical-align: middle;">{current_description}</td>',
                1
            )

        html_table += '</table>'
        return html_table

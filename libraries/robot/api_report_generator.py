import logging
import os
from typing import Dict, List
from jinja2 import FileSystemLoader, Environment, TemplateNotFound
from pandas import DataFrame
from libraries.common.utility_helpers import PROJECT_ROOT


class HTMLReportGenerator:
    def __init__(self, test_results: Dict[str, List[Dict]]):
        self.test_results = test_results
        self.templates_dir = os.path.join(PROJECT_ROOT, 'templates')

    def generate_html_report(self) -> str:
        """
        Generates the HTML report content.
        """
        try:
            file_loader = FileSystemLoader(self.templates_dir)
            env = Environment(loader=file_loader)
            template = env.get_template('api_report_template.html')

            flattened_data = self._flatten_results(self.test_results)
            df = DataFrame(flattened_data)

            # Reorder columns if needed
            df = df[
                [
                    "TCID",
                    "Description",  # Add Description column
                    "Type",
                    "Field",
                    "Pre Value",
                    "Post Value",
                    "Actual",
                    "Expected",
                    "Result",
                ]
            ]

            # Create the HTML table with merged cells and color-coded results
            html_table = self._create_html_table(df)

            return template.render(html_table=html_table)
        except TemplateNotFound as e:
            logging.error(f"HTMLReportGenerator: Template not found: {e}")
            raise
        except Exception as e:
            logging.error(f"HTMLReportGenerator: Error generating HTML report: {e}")
            raise

    def _flatten_results(self, test_results: Dict[str, List[Dict]]):
        """
        Flattens the test results data.
        """
        for tcid, results in test_results.items():
            for result in results:
                row = {
                    "TCID": tcid,
                    "Description": result.get("description", ""),  # Add description field
                    "Type": result["type"],
                    "Field": result["field"],
                    "Pre Value": '',
                    "Post Value": '',
                    "Actual": '',
                    "Expected": '',
                    "Result": '',
                }

                if result["type"] == "Dynamic Checks":
                    row["Pre Value"] = result["Pre Value"]
                    row["Post Value"] = result["Post Value"]
                    # Add sign to Actual and Expected differences, and format to two decimal places
                    row["Actual"] = f"{result['Actual Diff']:+0.2f}"
                    row["Expected"] = f"{result['Expected Diff']:+0.2f}"
                    row["Result"] = result["result"]
                elif result["type"] in ("Precheck Checks", "Postcheck Checks"):
                    row["Actual"] = result["Actual Value"]
                    row["Expected"] = result["Expected Value"]
                    row["Result"] = result["result"]
                elif result["type"] == "Assertions":
                    row["Actual"] = result["Actual Value"]
                    row["Expected"] = result["Expected Value"]
                    row["Result"] = result["result"]

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
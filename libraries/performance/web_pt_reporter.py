import os

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import logging
from libraries.common.utility_helpers import PROJECT_ROOT


class WebPerformanceReporter:
    def __init__(self, response_time_data, memory_usage_data):
        self.response_time_data = response_time_data
        self.memory_usage_data = memory_usage_data

    def generate_memory_usage_chart(self, case_id, case_name):
        df = pd.DataFrame(self.memory_usage_data)
        plt.figure(figsize=(10, 6))
        plt.plot(df["round"], df["used_MB"], marker="o", label="Used Memory (MB)", color="blue")
        plt.title(f"JavaScript Memory Usage Trend - Case ID: {case_id}, Case Name: {case_name}")
        plt.xlabel("Round")
        plt.ylabel("Memory (MB)")
        plt.grid()
        plt.legend()
        return self._save_fig_as_base64()

    def generate_response_time_statistics_chart(self, case_id, case_name):
        df = pd.DataFrame(self.response_time_data)
        stats = df.groupby("function_name").agg({"response_time": ["mean", "max"]})
        stats.columns = ["Mean", "Max"]
        stats.reset_index(inplace=True)

        stats.plot(kind="bar", x="function_name", figsize=(10, 6), colormap="coolwarm")
        plt.title(f"Response Time Statistics - Case ID: {case_id}, Case Name: {case_name}")
        plt.xlabel("Function Name")
        plt.ylabel("Time (s)")
        plt.grid(axis="y")
        plt.xticks(rotation=45)
        return self._save_fig_as_base64()

    def generate_response_time_trend_chart(self, case_id, case_name):
        df = pd.DataFrame(self.response_time_data)
        plt.figure(figsize=(10, 6))
        for func in df["function_name"].unique():
            func_data = df[df["function_name"] == func]
            plt.plot(func_data["round"], func_data["response_time"], marker="o", label=func)

        plt.title(f"Response Time Trend - Case ID: {case_id}, Case Name: {case_name}")
        plt.xlabel("Round")
        plt.ylabel("Response Time (s)")
        plt.legend(title="Function Points")
        plt.grid()
        return self._save_fig_as_base64()

    def generate_response_time_statistics_table(self, case_id, case_name):
        df = pd.DataFrame(self.response_time_data)
        stats = df.groupby("function_name").agg({
            "response_time": [
                lambda x: round(x.mean(), 2),
                lambda x: round(x.max(), 2),
                lambda x: round(x.min(), 2),
                lambda x: round(x.median(), 2),
                lambda x: round(x.quantile(0.9), 2),
                lambda x: round(x.quantile(0.95), 2),
                lambda x: round(x.quantile(0.99), 2)
            ]
        }).reset_index()

        stats.columns = ["Function Name", "Mean (s)", "Max (s)", "Min (s)",
                         "Median (s)", "P90 (s)", "P95 (s)", "P99 (s)"]

        fig, ax = plt.subplots(figsize=(10, len(stats) * 0.5))
        ax.axis("tight")
        ax.axis("off")
        table = plt.table(cellText=stats.values, colLabels=stats.columns, cellLoc="center", loc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.3, 1.5)
        plt.title(f"Response Time Statistics Table - Case ID: {case_id}, Case Name: {case_name}", y=1.1)
        return self._save_fig_as_base64()

    def save_to_csv(self):
        output_dir = os.path.join(PROJECT_ROOT, 'report')
        response_time_data_path = os.path.join(output_dir, 'response_time_data.csv')
        memory_usage_data_path = os.path.join(output_dir, 'memory_usage_data.csv')

        if self.response_time_data:
            response_time_df = pd.DataFrame(self.response_time_data)
            response_time_df.to_csv(response_time_data_path, index=False)
            logging.info("Response time data saved to 'response_time_data.csv'.")

        if self.memory_usage_data:
            memory_usage_df = pd.DataFrame(self.memory_usage_data)
            memory_usage_df.to_csv(memory_usage_data_path, index=False)
            logging.info("Memory usage data saved to 'memory_usage_data.csv'.")

    def _save_fig_as_base64(self):
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        base64_image = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close()
        return base64_image

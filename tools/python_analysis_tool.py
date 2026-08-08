"""
Module 10 — Python Tool.
Lets the agent compute statistics and build comparison tables,
e.g. 'Compare Revenue Growth' across companies.
"""
import json
import statistics
from langchain_core.tools import tool


@tool
def compare_metrics(data_json: str) -> str:
    """
    Compare a numeric metric across multiple entities and return a
    markdown table plus basic stats (mean, min, max, stdev).

    Input must be a JSON string shaped like:
    {"metric": "Revenue Growth %", "values": {"Google": 12.1, "Microsoft": 15.4, "Amazon": 11.0}}
    """
    try:
        payload = json.loads(data_json)
        metric = payload.get("metric", "Metric")
        values = payload.get("values", {})
        if not values:
            return "No values provided to compare."

        nums = list(values.values())
        rows = "\n".join(f"| {name} | {val} |" for name, val in values.items())
        table = f"| Entity | {metric} |\n|---|---|\n{rows}"

        stats = (
            f"Mean: {statistics.mean(nums):.2f}\n"
            f"Max: {max(values, key=values.get)} ({max(nums):.2f})\n"
            f"Min: {min(values, key=values.get)} ({min(nums):.2f})\n"
            f"Std dev: {statistics.pstdev(nums):.2f}" if len(nums) > 1 else ""
        )
        return f"{table}\n\n{stats}"
    except Exception as e:
        return f"Could not parse comparison input: {e}"

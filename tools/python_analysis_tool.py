"""
Module 4 — Python Analysis Tool.
Executes comparisons on financial or operational metrics.
"""
import json
from typing import Union, Dict
from langchain_core.tools import tool


@tool
def compare_metrics(metric: str, values: Union[Dict[str, float], str]) -> str:
    """
    Compare financial or operational metrics across multiple companies or entities.

    Args:
        metric: Name of the metric being compared (e.g., 'Gross Margin %', 'Revenue Growth').
        values: A dictionary mapping entity names to numerical values (e.g., {"Apple": 38.0, "Microsoft": 70.3}), 
                or a valid JSON string representing that dictionary.
    """
    try:
        # Handle string input if the model passes values as a JSON string
        if isinstance(values, str):
            try:
                values = json.loads(values)
            except json.JSONDecodeError:
                return f"Error: Could not parse values JSON string: {values}"

        if not isinstance(values, dict) or not values:
            return "No valid key-value pairs provided for metric comparison."

        lines = [f"**Comparison: {metric}**\n"]
        
        # Sort values in descending order
        sorted_entities = sorted(values.items(), key=lambda item: item[1], reverse=True)
        
        for rank, (entity, val) in enumerate(sorted_entities, 1):
            lines.append(f"{rank}. **{entity}**: {val}")

        return "\n".join(lines)

    except Exception as e:
        return f"Error analyzing metrics: {e}"
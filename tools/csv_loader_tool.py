"""csv_loader_tool — reads a CSV file from disk, returns list of dicts."""

import csv
import os
from langchain_core.tools import tool


@tool
def csv_loader_tool(file_path: str) -> list[dict]:
    """
    Read a CSV file from the given path and return its contents as a list of dicts.
    Raises FileNotFoundError if the file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]

"""
metadata_writer.py

Handles writing structured metadata to a tab-delimited text file.

Functions:
    - write_metadata(metadata, path, announce=lambda m: None):
        Writes a list of metadata dictionaries to a .tsv file with headers.
"""

import csv
from typing import List, Dict, Callable

def write_metadata(metadata: List[Dict[str, str]], path: str, announce: Callable[[str], None] = lambda m: None) -> None:   
    """
    Writes metadata records to a tab-separated file at the specified path.

    If the metadata list is empty, the function exits silently.
    Otherwise, it writes the header using the dictionary keys and saves all rows.

    Args:
        metadata (list[dict]): List of dictionaries containing metadata for each record.
        path (str): Destination path for the output .tsv file.
        announce (callable, optional): Callback function to announce completion. Defaults to a no-op.
    """
    if not metadata:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metadata[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(metadata)
    announce(f"Metadata written to {path}")

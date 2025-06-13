"""
block_utils.py

Provides helper functions for parsing ABI trace data blocks from text files 
and extracting values using regular expressions.

Functions:
    - parse_blocks(text): Splits raw trace content into discrete trace blocks using known delimiters.
    - safe_get(pat, block): Safely extracts the first matched group from a block using a regex pattern.
"""

import re
from typing import List

def parse_blocks(text: str) -> List[str]:    
    """
    Parses the input text into valid ABI trace blocks based on known start and end delimiters.

    Each block is expected to begin with a line starting '-1    NULL    CTG' and typically ends with '</Tracefile>'.
    Only blocks containing 'Tracefile' or '<FileName>' are retained.

    Args:
        text (str): The full text content to parse.

    Returns:
        list[str]: A list of strings, each representing a parsed block.
    """
    blocks, current = [], []
    for line in text.splitlines():
        if line.startswith("-1\tNULL\tCTG"):
            if current and any("Tracefile" in l or "<FileName>" in l for l in current):
                blocks.append("\n".join(current))
            current = [line]
        elif "</Tracefile>" in line:
            current.append(line)
            blocks.append("\n".join(current))
            current = []
        else:
            current.append(line)

    # Only append the last block if it contains valid trace content
    if current and any("Tracefile" in l or "<FileName>" in l for l in current):
        blocks.append("\n".join(current))

    return blocks

def safe_get(pat: str, block: str) -> str:
    """Returns the first regex group match from a block."""
    match = re.search(pat, block, re.DOTALL)
    return match.group(1) if match else ""
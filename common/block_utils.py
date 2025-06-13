import re

def parse_blocks(text):
    """Parses the input text into valid ABI trace blocks based on known delimiters."""
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

def safe_get(pat, block):
    """Returns the first regex group match from a block."""
    match = re.search(pat, block, re.DOTALL)
    return match.group(1) if match else ""
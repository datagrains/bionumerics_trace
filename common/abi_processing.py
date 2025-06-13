import re
import logging

logger = logging.getLogger(__name__)

def extract_base64_data(block):
    """Extracts base64 data from an ABI-style <Data> tag, logs cleanup steps."""
    match = re.search(r"<Data.*?>(.*?)</Data>", block, re.DOTALL)
    if not match:
        logger.info("🔍 No <Data> tag found — base64 may exist but is not ABI-formatted.")
        return ""

    raw_b64 = match.group(1)
    original_len = len(raw_b64)

    # Remove illegal characters
    cleaned = re.sub(r"[^A-Za-z0-9+/=]", "", raw_b64)
    cleaned_len = len(cleaned)
    if cleaned_len < original_len:
        logger.info(f"🧹 Removed {original_len - cleaned_len} invalid base64 characters.")

    # Pad to nearest multiple of 4
    padding = (-cleaned_len) % 4
    if padding:
        logger.info(f"🧩 Applied {padding} '=' padding characters for base64 alignment.")

    padded = cleaned + "=" * padding
    logger.info(f"✅ Prepared base64 string of length {len(padded)}.")
    return padded

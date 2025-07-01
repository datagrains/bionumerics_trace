"""
abi_processing.py

Utilities for handling ABI-formatted base64 data within sequencing trace files.

Functions:
    - extract_base64_data(block, try_decompress=True): Extracts, cleans, decodes, and optionally decompresses base64-encoded ABI data from a trace block.
    - has_abi_header(data): Checks whether the given binary data begins with the 'ABIF' header typical of ABI-formatted files.
"""

import re
import base64
import zlib
import logging
import os

logger = logging.getLogger(__name__)


def extract_base64_data(block: str, try_decompress: bool = True) -> bytes:
    """
    Extracts ABI-formatted base64 data from a trace block, cleans invalid characters,
    applies padding, decodes the base64 string, and optionally attempts zlib decompression.

    Args:
        block (str): The raw text block potentially containing base64-encoded data.
        try_decompress (bool): Whether to attempt zlib decompression after decoding. Defaults to True.

    Returns:
        bytes: The decoded (and optionally decompressed) binary data, or an empty byte string on failure.
    """
    match = re.search(r"<Data.*?>(.*?)</Data>", block, re.DOTALL)
    if not match:
        logger.info(
            "No <Data> tag found — base64 may exist but is not ABI-formatted.")
        return b""  # return raw bytes instead of string

    raw_b64 = match.group(1)
    original_len = len(raw_b64)

    cleaned = re.sub(r"[^A-Za-z0-9+/=]", "", raw_b64)
    cleaned_len = len(cleaned)
    if cleaned_len < original_len:
        logger.info(
            f"Removed {original_len - cleaned_len} invalid base64 characters.")

    padding = (-cleaned_len) % 4
    if padding:
        logger.info(
            f"Applied {padding} '=' padding characters for base64 alignment.")

    padded = cleaned + "=" * padding
    logger.info(f"Prepared base64 string of length {len(padded)}.")

    try:
        decoded = base64.b64decode(padded)
        logger.info(f"Base64 decoded successfully: {len(decoded)} bytes.")
    except Exception as e:
        logger.warning(f"Base64 decoding failed: {e}")
        return b""

    if try_decompress:
        try:
            decompressed = zlib.decompress(decoded)
            logger.info(
                f"Zlib decompression succeeded: {len(decompressed)} bytes.")
            return decompressed
        except zlib.error as e:
            logger.info(
                f"ℹBase64 data was not compressed or decompression failed: {e}")

    return decoded


def has_abi_header(data: bytes) -> bool:
    """
    Checks if the given binary data begins with the 'ABIF' header, indicating ABI format.

    Args:
        data (bytes): The binary data to inspect.

    Returns:
        bool: True if the data starts with the 'ABIF' signature, False otherwise.
    """
    return data[:4] == b'\x41\x42\x49\x46'  # or simply b'ABIF'


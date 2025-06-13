"""
image_tools.py

Provides tools for handling binary image-related operations. Includes functionality to:
- Save binary data to disk
- Render greyscale images from raw byte streams
- Detect and extract embedded image data within binary content

Functions:
    - save_binary_output(path, data, announce=lambda m: None, label="binary"):
        Saves raw binary data to the specified file path.
    - render_greyscale_image(data, path, width, announce=lambda m: None):
        Renders and saves a greyscale image from binary data given a target width.
    - find_embedded_image(binary):
        Scans binary content for recognizable image format headers and extracts the image if found.
"""

from typing import Callable, Tuple, Optional


def save_binary_output(path: str, data: bytes, announce: Callable[[str], None] = lambda m: None, label: str = "binary") -> None:
    """
    Saves binary data to a specified file path and announces the action using a callback.

    Args:
        path (str): File system path where the binary data will be saved.
        data (bytes): The binary content to be written to disk.
        announce (callable, optional): Callback function for status reporting. Defaults to a no-op.
        label (str, optional): Descriptive label for logging. Defaults to "binary".
    """
    with open(path, "wb") as f:
        f.write(data)
    announce(f"Saved {label}: {path}")


def render_greyscale_image(data: bytes, path: str, width: int, announce: Callable[[str], None] = lambda m: None) -> None:
    """
    Converts raw binary data into a greyscale image and saves it as a PNG.

    Args:
        data (bytes): Raw binary data interpreted as greyscale pixel values.
        path (str): Destination file path for the rendered image.
        width (int): Width of the resulting image. Height is calculated automatically.
        announce (callable, optional): Callback function for status updates.

    Raises:
        RuntimeError: If the greyscale conversion or rendering fails.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    try:
        height = len(data) // width
        arr = np.frombuffer(data[:width * height],
                            dtype=np.uint8).reshape((height, width))
        if arr.size == 0:
            raise ValueError("Decoded greyscale image is empty")
        plt.imsave(path, arr, cmap="gray")
        announce(f"Rendered image: {path}")
    except Exception as e:
        raise RuntimeError(f"Greyscale rendering error: {e}")


def find_embedded_image(binary: bytes) -> Tuple[Optional[str], Optional[bytes]]:
    """
    Scans binary content for known image file signatures and extracts the corresponding image segment.

    Supported formats include PNG, JPG, GIF (87a/89a), and BMP.

    Args:
        binary (bytes): Binary data potentially containing an embedded image.

    Returns:
        tuple[str | None, bytes | None]: A tuple containing:
            - The file extension string (e.g. 'png') if detected, or None
            - The extracted image bytes, or None if not found
    """
    signatures = {
        b"\x89PNG\r\n\x1a\n": (b"IEND", "png"),
        b"\xff\xd8\xff": (b"\xff\xd9", "jpg"),
        b"GIF89a": (b"\x003b", "gif"),
        b"GIF87a": (b"\x003b", "gif"),
        b"BM": (None, "bmp"),
    }
    for sig, (end, ext) in signatures.items():
        i = binary.find(sig)
        if i != -1:
            j = binary.find(end, i) + len(end) if end else None
            return ext, binary[i:j] if j else binary[i:]
    return None, None

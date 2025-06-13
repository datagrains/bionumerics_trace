import os
import numpy as np
import matplotlib.pyplot as plt

def save_binary_output(path, data, announce=lambda m: None, label="binary"):
    with open(path, "wb") as f:
        f.write(data)
    announce(f"💾 Saved {label}: {path}")

def render_grayscale_image(data, path, width, announce=lambda m: None):
    import numpy as np
    import matplotlib.pyplot as plt

    try:
        height = len(data) // width
        arr = np.frombuffer(data[:width * height], dtype=np.uint8).reshape((height, width))
        if arr.size == 0:
            raise ValueError("Decoded grayscale image is empty")
        plt.imsave(path, arr, cmap="gray")
        announce(f"🖼️ Rendered image: {path}")
    except Exception as e:
        raise RuntimeError(f"Grayscale rendering error: {e}")

def find_embedded_image(binary):
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

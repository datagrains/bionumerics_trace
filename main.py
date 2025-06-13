import os
import base64
from common.logging_setup import setup_logging
from common.block_utils import parse_blocks, safe_get
from common.abi_processing import extract_base64_data
from common.image_tools import (
    save_binary_output,
    render_grayscale_image,
    find_embedded_image
)
from common.metadata_writer import write_metadata

logger = setup_logging()
announce = lambda m: logger.info(m.encode("ascii", "ignore").decode())
warn     = lambda m: logger.warning(m.encode("ascii", "ignore").decode())
fail     = lambda m: logger.error(m.encode("ascii", "ignore").decode())

def process_all_blocks(input_file, output_root, width_hint=512):
    dirs = {
        "bin": os.path.join(output_root, "abi_output"),
        "img": os.path.join(output_root, "grayscale_explorations"),
        "ext": os.path.join(output_root, "embedded_images"),
    }
    meta_path = os.path.join(output_root, "trace_metadata.tsv")
    for d in [*dirs.values(), os.path.dirname(meta_path)]:
        os.makedirs(d, exist_ok=True)

    with open(input_file, encoding="utf-8", errors="ignore") as f:
        blocks = [b for b in parse_blocks(f.read()) if b.strip()]

    metadata = []

    for i, block in enumerate(blocks, 1):
        tid = safe_get(r"\t(\d{6,}CTG\d+)\t", block) or safe_get(r"<FileName>(.*?)</FileName>", block) or f"block_{i}"
        raw_name = safe_get(r"<FileName>(.*?)</FileName>", block)
        fname = os.path.basename(raw_name) if raw_name else f"{tid}.ab1"
        status = "success"

        b64 = extract_base64_data(block)
        logger.debug(f"[Block {i} | {tid}] Raw extracted base64 (first 100 chars): {b64[:100]}")

        try:
            data = base64.b64decode(b64) if b64 else b""
            if not b64:
                status = "no base64 data"
                warn(f"❌ [Block {i} | {tid}] No base64 data. Continuing with empty payload.")
            else:
                announce(f"🔍 [Block {i} | {tid}] Base64 decoded successfully.")

        except Exception as e:
            data = b""
            status = f"base64 decoding error: {e}"
            fail(f"⚠️ [Block {i} | {tid}] Base64 decoding failed: {e}")

        # Save placeholder or actual ABI binary
        save_binary_output(os.path.join(dirs["bin"], fname), data, announce)
        if not data:
            warn(f"⚠️ [Block {i} | {tid}] Saved placeholder binary — decode failed, file contains no usable data.")

        # Attempt grayscale rendering
        grayscale_path = os.path.join(dirs["img"], f"{os.path.splitext(fname)[0]}_rendered.png")
        announce(f"🖼️ [Block {i} | {tid}] Attempting grayscale rendering...")
        try:
            render_grayscale_image(data, grayscale_path, width_hint, announce)
        except Exception as e:
            warn(f"❌ [Block {i} | {tid}] Grayscale render failed: {e}")

        # Attempt embedded image extraction
        announce(f"🔎 [Block {i} | {tid}] Checking for embedded chromatogram image...")
        try:
            ext, img = find_embedded_image(data)
            if img:
                announce(f"📸 [Block {i} | {tid}] Embedded image found — attempting to save...")
                try:
                    save_binary_output(
                        os.path.join(dirs["ext"], f"{os.path.splitext(fname)[0]}_trace.{ext}"),
                        img,
                        announce,
                        label="embedded image"
                    )
                except Exception as e:
                    warn(f"❌ [Block {i} | {tid}] Failed to save embedded image: {e}")
            else:
                warn(f"⚠️ [Block {i} | {tid}] No embedded image could be extracted from ABI data.")
        except Exception as e:
            fail(f"❌ [Block {i} | {tid}] Error during embedded image extraction: {e}")

        announce(f"📦 [Block {i} | {tid}] Completed with status: {status}")

        metadata.append({
            "Block": i,
            "TRACEID": tid,
            "FileName": raw_name or "",
            "FileType": safe_get(r"<FileType>(.*?)</FileType>", block),
            "Name": safe_get(r"<Name>(.*?)</Name>", block),
            "Trim1": safe_get(r'Trim1="(\d+)"', block),
            "Trim2": safe_get(r'Trim2="(\d+)"', block),
            "UsedRegions": safe_get(r"<UsedRegions>(.*?)</UsedRegions>", block),
            "Alignment": safe_get(r"<Align.*?>(.*?)</Align>", block),
        })

    write_metadata(metadata, meta_path, announce)

if __name__ == "__main__":
    process_all_blocks("data/inputs/SEQTRACEFILES_TAB_delimited.txt", "data/outputs", 512)

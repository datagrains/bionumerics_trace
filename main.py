import os
import base64
import yaml
from common.logging_setup import setup_logging
from common.block_utils import parse_blocks, safe_get
from common.abi_processing import extract_base64_data, has_abi_header
from common.image_tools import save_binary_output, render_greyscale_image, find_embedded_image
from common.metadata_writer import write_metadata
import matplotlib
import numpy

logger = setup_logging()

def log(lvl, msg): 
    return getattr(logger, lvl)(msg.encode("ascii", "ignore").decode())

def load_config(config_path: str) -> dict:
    """
    Loads configuration from a YAML file.
    
    Args:
        config_path (str): Path to the YAML configuration file.
    
    Returns:
        dict: Configuration parameters.
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config or {}
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        raise

def process_all_blocks(config: dict) -> None:
    """
    Processes all trace data blocks using configuration from YAML file.

    Steps performed:
    - Parses the input file into blocks.
    - Extracts and decodes base64 ABI content from each block.
    - Saves binary data to an output folder.
    - Attempts to render greyscale previews of the binary content.
    - Searches for and extracts any embedded chromatogram images.
    - Logs detailed info and warnings throughout the process.
    - Writes extracted metadata to a .tsv file.

    Args:
        config (dict): Configuration dictionary containing input_path, output_root, and width_hint.
    """
    input_path = config.get("input_path")
    output_root = config.get("output_root", "data/outputs")
    width_hint = config.get("width_hint", 512)

    if not input_path:
        raise ValueError("input_path must be specified in the configuration")

    dirs = {
        "bin": os.path.join(output_root, "abi_output"),
        "img": os.path.join(output_root, "grayscale_explorations"),
        "ext": os.path.join(output_root, "embedded_images"),
    }
    meta_path = os.path.join(output_root, "trace_metadata.tsv")
    [os.makedirs(d, exist_ok=True) for d in (*dirs.values(), os.path.dirname(meta_path))]

    with open(input_path, encoding="utf-8", errors="ignore") as f:
        blocks = [b for b in parse_blocks(f.read()) if b.strip()]

    metadata = []

    for i, block in enumerate(blocks, 1):
        tid = safe_get(r"\t(\d{6,}CTG\d+)\t", block) or safe_get(
            r"<FileName>(.*?)</FileName>", block) or f"block_{i}"
        raw_name = safe_get(r"<FileName>(.*?)</FileName>", block)
        fname = os.path.basename(raw_name) if raw_name else f"{tid}.ab1"
        status, data = "success", b""

        b64 = extract_base64_data(block)
        logger.debug(f"[Block {i} | {tid}] Raw extracted base64 (first 100 chars): {b64[:100]}")

        try:
            data = base64.b64decode(b64) if b64 else b""
            if not b64:
                status = "no base64 data"
                log("warning", f"[Block {i} | {tid}] No base64 data.")
            else:
                log("info", f"[Block {i} | {tid}] Base64 decoded successfully.")
                if has_abi_header(data):
                    log("info", f"[Block {i} | {tid}] ABI header detected.")
                else:
                    log("warning", f"[Block {i} | {tid}] ABI header not found.")
        except Exception as e:
            status = f"base64 decoding error: {e}"
            log("error", f"[Block {i} | {tid}] Base64 decoding failed: {e}")

        save_binary_output(os.path.join(dirs["bin"], fname), data, lambda m: log("info", m))
        if not data:
            log("warning", f"[Block {i} | {tid}] Saved placeholder binary.")

        log("info", f"[Block {i} | {tid}] Attempting greyscale rendering...")
        try:
            render_greyscale_image(data, os.path.join(
                dirs["img"], f"{os.path.splitext(fname)[0]}_rendered.png"), width_hint, lambda m: log("info", m))
        except Exception as e:
            log("warning", f"[Block {i} | {tid}] Grayscale render failed: {e}")

        log("info", f"[Block {i} | {tid}] Checking for embedded chromatogram image...")
        try:
            ext, img = find_embedded_image(data)
            if img:
                log("info", f"[Block {i} | {tid}] Embedded image found.")
                try:
                    save_binary_output(os.path.join(dirs["ext"], f"{os.path.splitext(fname)[0]}_trace.{ext}"), img, 
                                     lambda m: log("info", m), label="embedded image")
                except Exception as e:
                    log("warning", f"[Block {i} | {tid}] Failed to save embedded image: {e}")
            else:
                log("warning", f"[Block {i} | {tid}] No embedded image found.")
        except Exception as e:
            log("error", f"[Block {i} | {tid}] Error during image extraction: {e}")

        log("info", f"[Block {i} | {tid}] Completed with status: {status}")

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

    write_metadata(metadata, meta_path, lambda m: log("info", m))

if __name__ == "__main__":
    config = load_config("config.yaml")
    process_all_blocks(config)
    print(f"matplotlib version: {matplotlib.__version__}")
    print(f"numpy version: {numpy.__version__}")
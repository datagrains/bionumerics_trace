# import os
# import base64
# import yaml
# import matplotlib
# import numpy
# from common.logging_setup import setup_logging
# from common.block_utils import parse_blocks, safe_get
# from common.abi_processing import extract_base64_data, has_abi_header, is_ab1_file, list_ab1_files
# from common.image_tools import save_binary_output, render_greyscale_image, find_embedded_image
# from common.metadata_writer import write_metadata

# logger = setup_logging()

# def log(lvl, msg): 
#     return getattr(logger, lvl)(msg.encode("ascii", "ignore").decode())

# def load_config(config_path: str) -> dict:
#     try:
#         with open(config_path, 'r') as f:
#             config = yaml.safe_load(f)
#         return config or {}
#     except Exception as e:
#         logger.error(f"Failed to load config from {config_path}: {e}")
#         raise

# def process_data_sources(config: dict) -> None:
#     input_path = config.get("input_path")
#     output_root = config.get("output_root", "data/outputs")
#     width_hint = config.get("width_hint", 512)

#     if not input_path:
#         raise ValueError("input_path must be specified in the configuration")

#     dirs = {
#         "bin": os.path.join(output_root, "abi_output"),
#         "img": os.path.join(output_root, "grayscale_explorations"),
#         "ext": os.path.join(output_root, "embedded_images"),
#     }
#     meta_path = os.path.join(output_root, "trace_metadata.tsv")
#     [os.makedirs(d, exist_ok=True) for d in (*dirs.values(), os.path.dirname(meta_path))]

#     metadata = []
#     blocks = []

#     # Detect raw AB1 files
#     ab1_paths = []
#     if os.path.isdir(input_path):
#         ab1_paths = list_ab1_files(input_path)
#     elif is_ab1_file(input_path):
#         ab1_paths = [input_path]
#     else:
#         with open(input_path, encoding="utf-8", errors="ignore") as f:
#             blocks = [b for b in parse_blocks(f.read()) if b.strip()]

#     # Process raw AB1 files
#     for i, ab1_file in enumerate(ab1_paths, 1):
#         tid = os.path.splitext(os.path.basename(ab1_file))[0]
#         status = "raw ab1"
#         with open(ab1_file, "rb") as f:
#             data = f.read()
#         log("info", f"[AB1 {i} | {tid}] Loaded raw .ab1 file.")
#         output_name = f"{tid}.ab1"

#         save_binary_output(os.path.join(dirs["bin"], output_name), data, lambda m: log("info", m))
#         try:
#             render_greyscale_image(data, os.path.join(
#                 dirs["img"], f"{tid}_rendered.png"), width_hint, lambda m: log("info", m))
#         except Exception as e:
#             log("warning", f"[AB1 {i} | {tid}] Greyscale render failed: {e}")

#         try:
#             ext, img = find_embedded_image(data)
#             if img:
#                 save_binary_output(os.path.join(dirs["ext"], f"{tid}_trace.{ext}"), img, lambda m: log("info", m))
#         except Exception as e:
#             log("error", f"[AB1 {i} | {tid}] Embedded image extraction failed: {e}")

#         metadata.append({
#             "Block": i,
#             "TRACEID": tid,
#             "FileName": ab1_file,
#             "FileType": "AB1",
#             "Name": "",
#             "Trim1": "",
#             "Trim2": "",
#             "UsedRegions": "",
#             "Alignment": "",
#         })

#     # Process base64-embedded blocks (same as your original logic)
#     for i, block in enumerate(blocks, len(ab1_paths) + 1):
#         tid = safe_get(r"\t(\d{6,}CTG\d+)\t", block) or safe_get(
#             r"<FileName>(.*?)</FileName>", block) or f"block_{i}"
#         raw_name = safe_get(r"<FileName>(.*?)</FileName>", block)
#         fname = os.path.basename(raw_name) if raw_name else f"{tid}.ab1"
#         status, data = "success", b""

#         b64 = extract_base64_data(block)
#         try:
#             data = base64.b64decode(b64) if b64 else b""
#             if not b64:
#                 status = "no base64 data"
#             elif not has_abi_header(data):
#                 status = "no abi header"
#         except Exception as e:
#             status = f"decode error: {e}"

#         save_binary_output(os.path.join(dirs["bin"], fname), data, lambda m: log("info", m))
#         try:
#             render_greyscale_image(data, os.path.join(
#                 dirs["img"], f"{os.path.splitext(fname)[0]}_rendered.png"), width_hint, lambda m: log("info", m))
#         except:
#             pass

#         try:
#             ext, img = find_embedded_image(data)
#             if img:
#                 save_binary_output(os.path.join(dirs["ext"], f"{os.path.splitext(fname)[0]}_trace.{ext}"), img, 
#                                    lambda m: log("info", m))
#         except:
#             pass

#         metadata.append({
#             "Block": i,
#             "TRACEID": tid,
#             "FileName": raw_name or "",
#             "FileType": safe_get(r"<FileType>(.*?)</FileType>", block),
#             "Name": safe_get(r"<Name>(.*?)</Name>", block),
#             "Trim1": safe_get(r'Trim1="(\d+)"', block),
#             "Trim2": safe_get(r'Trim2="(\d+)"', block),
#             "UsedRegions": safe_get(r"<UsedRegions>(.*?)</UsedRegions>", block),
#             "Alignment": safe_get(r"<Align.*?>(.*?)</Align>", block),
#         })

#     write_metadata(metadata, meta_path, lambda m: log("info", m))

# if __name__ == "__main__":
#     config = load_config("config.yaml")
#     process_data_sources(config)
#     print(f"matplotlib version: {matplotlib.__version__}")
#     print(f"numpy version: {numpy.__version__}")



from Bio import SeqIO
import matplotlib.pyplot as plt
import os

def plot_chromatogram(ab1_path, output_filename="chromatogram.png"):
    record = SeqIO.read(ab1_path, "abi")

    # ABI channels: G (data9), A (data10), T (data11), C (data12)
    channels = {
        'G': record.annotations['abif_raw']['DATA9'],
        'A': record.annotations['abif_raw']['DATA10'],
        'T': record.annotations['abif_raw']['DATA11'],
        'C': record.annotations['abif_raw']['DATA12']
    }

    x = range(len(channels['G']))
    plt.figure(figsize=(14, 4))
    for base, signal in channels.items():
        plt.plot(x, signal, label=base)
    plt.title("ABI Chromatogram Trace")
    plt.xlabel("Data Points")
    plt.ylabel("Signal Intensity")
    plt.legend()
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("data/outputs", exist_ok=True)
    plt.savefig(os.path.join("data/outputs", output_filename))
    plt.close()

# Usage
plot_chromatogram("data/inputs/B.bacilliformis_CSH1f.ab1")

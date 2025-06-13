import csv

def write_metadata(metadata, path, announce=lambda m: None):
    if not metadata:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metadata[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(metadata)
    announce(f"📝 Metadata written to {path}")

import os
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.Restriction import RestrictionBatch
from sangerseq_viewer import sangerseq_viewer
import matplotlib.font_manager as fm
import patchworklib as pw
from QUEEN.queen import *
from QUEEN import cutsite
import numpy as np

# Input filenames (without extensions)
ab1_files = [
    "B_bacilliformis_CSH1f",
    "Spec_2xU6gRNA_1",
    "B.bacilliformis_BhCS1137n",
    "B.bacilliformis_CS140f",
    "B.bacilliformis_CS443f",
]

# Directories
input_dir = "data/inputs/ab1_files"
output_dir_genbank = "data/outputs/extracted_genbank_files"
output_dir_images = "data/outputs/trace_images"

# Build full paths to .ab1 files
ab1_paths = [os.path.join(input_dir, f"{filename}.ab1") for filename in ab1_files]

def trim_ab1_by_quality(record, threshold=20, min_run=5):
    qualities = record.letter_annotations["phred_quality"]
    sequence = str(record.seq)

    start = None
    for i in range(len(qualities) - min_run):
        if all(q >= threshold for q in qualities[i:i+min_run]):
            start = i
            break

    end = None
    for i in range(len(qualities) - min_run, 0, -1):
        if all(q >= threshold for q in qualities[i:i+min_run]):
            end = i + min_run
            break

    if start is None or end is None or start >= end:
        return None

    return sequence[start:end]

def convert_ab1_to_genbank(ab1_files, output_dir=output_dir_genbank):
    os.makedirs(output_dir, exist_ok=True)
    failed_files = []

    for ab1_file in ab1_files:
        try:
            record = SeqIO.read(ab1_file, "abi")
            trimmed_sequence = trim_ab1_by_quality(record)

            if not trimmed_sequence or len(trimmed_sequence) < 1:
                raise ValueError("No valid trimmed sequence found.")

            base_name = os.path.splitext(os.path.basename(ab1_file))[0]
            gb_filename = f"{base_name}_extracted.gb"
            gb_filepath = os.path.join(output_dir, gb_filename)

            gb_record = SeqRecord(
                Seq(trimmed_sequence),
                id=base_name,
                name="sanger_seq",
                description="Quality-trimmed from .ab1 file",
                annotations={
                    "molecule_type": "ds-DNA",
                    "topology": "linear",
                    "date": "04-AUG-2025",
                    "organism": "Bartonella bacilliformis"
                }
            )

            gb_record.features.append(
                SeqFeature(
                    FeatureLocation(start=0, end=len(trimmed_sequence)),
                    type="source",
                    qualifiers={
                        "organism": "Bartonella bacilliformis",
                        "mol_type": "genomic DNA",
                        "note": "Quality-trimmed sequence"
                    }
                )
            )

            gb_record.features.append(
                SeqFeature(
                    FeatureLocation(start=0, end=len(trimmed_sequence)),
                    type="gene",
                    qualifiers={"gene": "placeholder_gene"}
                )
            )

            with open(gb_filepath, "w") as output_handle:
                SeqIO.write(gb_record, output_handle, "genbank")

            print(f"Saved GenBank: {gb_filepath}")

        except Exception as e:
            print(f"Failed to process {ab1_file}: {e}")
            failed_files.append(ab1_file)

    if failed_files:
        print("\nSummary of failed files:")
        for f in failed_files:
            print(f" - {f}")
    else:
        print("\nAll files processed successfully.")

def process_sanger_sequences(samples, linebreak=200, start=None, end=None):
    os.makedirs(output_dir_images, exist_ok=True)

    for sample in samples:
        try:
            if not os.path.exists(sample["gbkpath"]) or os.path.getsize(sample["gbkpath"]) == 0:
                print(f"Skipping {sample['gbkpath']} — file missing or empty.")
                continue

            fig = sangerseq_viewer.view_sanger(
                gbkpath=sample["gbkpath"],
                abipath=sample["abipath"],
                output=sample["output"],
                linebreak=linebreak,
                start=start,
                end=end
            )
            fig.savefig(sample["output"], dpi=200, bbox_inches="tight")
            print(f"Success: Saved Trace Image: {sample['output']}")
        except Exception as e:
            print(f"Fail: Could not generate trace for {sample['abipath']}: {e}")

# Step 1: Convert AB1 files to GenBank
convert_ab1_to_genbank(ab1_paths)

# Step 2: Build samples list
samples = []
for filename in ab1_files:
    gb_path = os.path.join(output_dir_genbank, f"{filename}_extracted.gb")
    if os.path.exists(gb_path) and os.path.getsize(gb_path) > 0:
        samples.append({
            "gbkpath": gb_path,
            "abipath": os.path.join(input_dir, f"{filename}.ab1"),
            "output": os.path.join(output_dir_images, f"{filename}_extracted.png")
        })

# Step 3: Generate trace plots (called only once)
process_sanger_sequences(samples)

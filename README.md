# BioNumerics Trace

## Overview

This Python-based script suite processes tab-delimited text files containing Base64 encoded sequencing trace data. It is designed to extract, decode, and analyse base64-encoded trace blocks exported from sequencing systems, and to produce structured binary files, image visualisations, and metadata summaries.

## Features

- **Block Parsing**: Extracts ABI trace blocks based on recognisable delimiters.
- **Base64 Decoding & ABI Validation**: Cleans and decodes base64 payloads, and verifies the ABI file format using the ASCII header `ABIF` (hex: `41 42 49 46`).
- **Binary Output**: Saves decoded content as `.ab1` files, including empty placeholders when decoding fails.
- **Greyscale Rendering**: Converts binary data into greyscale image visualisations using NumPy and Matplotlib.
- **Embedded Image Extraction**: Scans decoded data for embedded image signatures (PNG, JPG, GIF, BMP) and exports them if found.
- **Metadata Export**: Generates a tab-separated metadata file (`trace_metadata.tsv`) capturing key fields extracted from each trace block.


## Logging

A structured logging system is implemented using Python’s `logging` module. Features include:

- File and console logging with level-aware handlers.
- Informative logs at each step of the processing pipeline.
- Warnings and error messages on decoding failures, rendering issues, and validation misses.
- Optional integration of custom `announce()` functions for flexible output control.


## Unit Tests

The suite includes unit tests for each module using Python’s `unittest` framework. Coverage includes:

- Text and regex-based block extraction and parsing.
- File and image output handling with mocked I/O.
- Validation of log configuration and message routing.
- Metadata writing logic with header and data verification.
- Detection of embedded content and ABI headers.

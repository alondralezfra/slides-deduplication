#!/usr/bin/env python3

import argparse
import sys
import os
import fitz  # PyMuPDF

# -------------------------
# Text utilities
# -------------------------

def normalize(text):
    return " ".join(text.lower().split())

def text_overlap_ratio(a, b):
    """
    How much of A is contained in B (word-wise)
    """
    set_a = set(a.split())
    set_b = set(b.split())

    if not set_a:
        return 0.0

    return len(set_a & set_b) / len(set_a)

def is_redundant(prev_text, curr_text, threshold):
    """
    prev is redundant if it's mostly contained in curr
    and curr has more content
    """
    if len(curr_text) <= len(prev_text):
        return False

    overlap = text_overlap_ratio(prev_text, curr_text)
    return overlap >= threshold

# -------------------------
# PDF processing
# -------------------------

def clean_pdf(input_path, output_path, threshold, dry_run=False, verbose=False):
    doc = fitz.open(input_path)
    texts = [normalize(doc.load_page(i).get_text("text"))
             for i in range(len(doc))]

    keep_indices = []

    for i in range(len(texts)):
        if i == len(texts) - 1:
            keep_indices.append(i)
            continue

        if is_redundant(texts[i], texts[i+1], threshold):
            if verbose:
                print(f"Removing slide {i + 1} (merged into {i + 2})")
            continue
        else:
            keep_indices.append(i)

    if dry_run:
        removed = set(range(len(texts))) - set(keep_indices)
        print(f"Slides to remove: {[i + 1 for i in sorted(removed)]}")
        return

    new_doc = fitz.open()
    for i in keep_indices:
        new_doc.insert_pdf(doc, from_page=i, to_page=i)

    new_doc.save(output_path)
    new_doc.close()
    doc.close()

    print(f"Saved cleaned PDF: {output_path}")
    print(f"Slides kept: {len(keep_indices)} / {len(texts)}")

# -------------------------
# CLI
# -------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Remove redundant incremental slides from a PDF slide deck."
    )

    parser.add_argument("input", help="Input PDF file")
    parser.add_argument(
        "--out", "-o",
        help="Output PDF file"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.9,
        help="Text overlap threshold (default: 0.9)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show slides that would be removed without creating a PDF"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed decisions"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output = args.out
    if not output:
        base, ext = os.path.splitext(args.input)
        output = f"{base}_cleaned.pdf"

    clean_pdf(
        args.input,
        output,
        threshold=args.threshold,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

if __name__ == "__main__":
    main()
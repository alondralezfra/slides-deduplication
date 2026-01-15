#!/usr/bin/env python

import argparse
import sys
import os
import fitz  # requires installation of PyMuPDF

# Helper Text functions

def normalize(text):
    """
    Convert text to lowercase and remove extra whitespace
    
    :param text: the string to be normalized
    """
    return " ".join(text.lower().split())

def text_overlap_ratio(a, b):
    """
    Returns percentage of words in string a that are in string b
    
    :param a: string to be evaluated
    :param b: string used to evalute a
    """
    set_a = set(a.split())
    set_b = set(b.split())

    if not set_a:
        return 0.0

    return len(set_a & set_b) / len(set_a)

def is_redundant(prev_text, curr_text, threshold):
    """
    Returns whether the string prev_text contains words mostly
    included in the string curr_text
    
    :param prev_text: string containing previous text
    :param curr_text: string containing current text
    :param threshold: float representing the minimum percentage of prev_text that must be in curr_text
    """
    if len(curr_text) <= len(prev_text):
        return False

    overlap = text_overlap_ratio(prev_text, curr_text)
    return overlap >= threshold

# PDF processing

def clean_pdf(input_path, output_path, threshold, dry_run=False, verbose=False):
    """
    Loops through pages of the PDF and removes pages whose text is mostly contained in the following page
    
    :param input_path: string path containing the PDF
    :param output_path: string path which should contain the cleaned PDF
    :param threshold: minimum percentage of text contained in next page for the current page to be considered redundant
    :param dry_run: boolean 
    :param verbose: boolean for verbose mode
    """
    # Open PDF and turn into normalized list of pages
    doc = fitz.open(input_path)
    texts = [normalize(doc.load_page(i).get_text("text"))
             for i in range(len(doc))]

    # Initialize list containing indices of the pages we are to keep (non-redundant pages)
    keep_indices = []

    # Iterate over pages
    for i in range(len(texts)):

        # If at last page, keep and skip iteration to prevent indexing error
        if i == len(texts) - 1:
            keep_indices.append(i)
            continue

        # If current page text is mostly contained in the next page, remove it
        if is_redundant(texts[i], texts[i+1], threshold):
            if verbose:
                print(f"Removing slide {i + 1} (merged into {i + 2})")
            continue

        # Otherwise keep the page
        else:
            keep_indices.append(i)

    if dry_run:
        # Set of indices of pages that were removed
        removed = set(range(len(texts))) - set(keep_indices)
        print(f"Slides to remove: {[i + 1 for i in sorted(removed)]}")
        return

    # Add the kept pages to a new PDF
    new_doc = fitz.open()
    for i in keep_indices:
        new_doc.insert_pdf(doc, from_page=i, to_page=i)

    # Save the new PDF in the specified path and close the PDF documents
    new_doc.save(output_path)
    new_doc.close()
    doc.close()

    print(f"Saved cleaned PDF: {output_path}")
    print(f"Slides kept: {len(keep_indices)} / {len(texts)}")

# CLI

def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(
        description="Remove redundant incremental slides from a PDF slide deck."
    )

    # Add arguments for input path, output path, threshold, dry run, and verbose
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

    # Parse arguments
    args = parser.parse_args()

    # If input path does not exist, exit with error
    if not os.path.exists(args.input):
        print(f"File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # If output path does not exist, exit with error
    output = args.out
    if not output:
        base, ext = os.path.splitext(args.input)
        output = f"{base}_cleaned.pdf"

    # Clean the PDF and place at output path
    clean_pdf(
        args.input,
        output,
        threshold=args.threshold,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

if __name__ == "__main__":
    main()
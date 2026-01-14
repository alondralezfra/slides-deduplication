# cleanpdf

**cleanpdf** is a command-line tool that removes redundant and incremental slides from PDF slide decks.

Many lecture PDFs contain dozens of nearly identical slides because instructors reveal bullet points or code line-by-line. This tool automatically collapses those sequences and keeps only the most complete version of each slide.

---

## Features

- Removes redundant / near-duplicate slides
- Collapses incremental bullet and code reveals
- Designed for **CS and text-heavy lecture slides**
- Single-file executable script
- Fast and lightweight (no ML required)

---

## Example

**Before:**  
80 slides (incremental bullet reveals)

**After:**  
25 slides (only final versions)

---

## Installation

### Requirements
- Python 3.8+
- PyMuPDF

Install dependency:
```bash
pip install pymupdf
```

### Setup

Save the script as cleanpdf

Make it executable:

```bash
chmod +x cleanpdf
```

(Optional) Move it into a directory on your $PATH, e.g.:

```bash
mv cleanpdf ~/bin/
```
---

# Usage
## Basic usage
```bash
cleanpdf slides.pdf
```

This creates:

slides_cleaned.pdf

Specify output file
```bash
cleanpdf slides.pdf --out cleaned.pdf
```

Adjust redundancy sensitivity
```bash
cleanpdf slides.pdf --threshold 0.85
```

Lower threshold = more aggressive removal.

Dry run (no PDF generated)
```bash
cleanpdf slides.pdf --dry-run
```

Shows which slides would be removed.

Verbose mode
```bash
cleanpdf slides.pdf --verbose
```

Prints detailed decisions during processing.

---

# How it works

For each pair of consecutive slides:

Extracts and normalizes text

Compares word overlap

If most of slide N's text appears in slide N+1, and slide N+1 contains more content:

Slide N is removed

The final PDF keeps only the most complete slides

This approach works well for:

Bullet-point reveals

Incremental code blocks

Definitions → examples → proofs

# Command-line options
Flag	Description	Default
--out, -o	Output PDF path	<input>_cleaned.pdf
--threshold, -t	Text overlap threshold	0.9
--dry-run	Show removals only	Off
--verbose, -v	Print decisions	Off
Limitations

Best for text-heavy slides

May not detect subtle changes in diagrams or equations

Assumes redundancy happens between adjacent slides

(These can be improved with image hashing in future versions.)

Future improvements

Visual similarity fallback for math-heavy slides

Header/footer detection and removal

Batch processing of directories

pipx / pip packaging
import pymupdf  # PyMuPDF
import pathlib
import json
import re

CORPUS_DIR = pathlib.Path("corpus/")
OUTPUT_FILE = pathlib.Path("data/parsed.jsonl")

# Matches a bare heading marker line, e.g. "I.", "II.", "A.", "1."
MARKER_PATTERN = re.compile(r"^\s*(?:[IVXLC]+\.|[A-Z]\.|\d+\.)\s*$")
# Matches a marker AND heading text together on one line, e.g. "I. INTRODUCTION"
INLINE_PATTERN = re.compile(r"^\s*(?:[IVXLC]+\.|[A-Z]\.|\d+\.)\s+\S.*$")


def extract_headings(lines):
    """Return a list of (line_index, heading_text) for every heading found."""
    headings = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if INLINE_PATTERN.match(line):
            headings.append((i, line))
        elif MARKER_PATTERN.match(line):
            # Look ahead for the next non-empty line as the heading text
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                combined = f"{line} {lines[j].strip()}"
                headings.append((i, combined))
        i += 1
    return headings


def parse_pdf(path: pathlib.Path):
    doc = pymupdf.open(path)
    records = []
    current_heading = "Unknown Section"

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if not text.strip():
            continue

        lines = text.split("\n")
        headings = extract_headings(lines)
        if headings:
            # Use the LAST heading found on this page as the section context
            current_heading = headings[-1][1]

        records.append({
            "source": path.name,
            "page": page_num,
            "section": current_heading,
            "text": text.strip(),
        })

    doc.close()
    return records


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    all_records = []

    pdf_files = sorted(CORPUS_DIR.glob("*.pdf"))
    print(f"Parsing {len(pdf_files)} PDFs...")

    for pdf_path in pdf_files:
        try:
            records = parse_pdf(pdf_path)
            all_records.extend(records)
            print(f"  {pdf_path.name}: {len(records)} pages parsed")
        except Exception as e:
            print(f"  FAILED: {pdf_path.name} ({e})")

    with open(OUTPUT_FILE, "w") as f:
        for record in all_records:
            f.write(json.dumps(record) + "\n")

    print(f"\nDone. {len(all_records)} page-records written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

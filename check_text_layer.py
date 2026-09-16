import fitz  # PyMuPDF
import pathlib

corpus_dir = pathlib.Path("corpus/")
flagged = []

for p in sorted(corpus_dir.glob("*.pdf")):
    doc = fitz.open(p)
    chars = sum(len(pg.get_text()) for pg in doc)
    avg_chars_per_page = chars / doc.page_count if doc.page_count else 0
    if avg_chars_per_page < 200:
        print(f"NO TEXT LAYER — drop or OCR: {p.name} (avg {avg_chars_per_page:.0f} chars/page)")
        flagged.append(p.name)
    doc.close()

print(f"\n{len(flagged)} of {len(list(corpus_dir.glob('*.pdf')))} PDFs flagged as no-text-layer.")

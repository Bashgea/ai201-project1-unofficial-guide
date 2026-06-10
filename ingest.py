"""
Document ingestion and chunking pipeline.
Loads PDFs from documents/, cleans extracted text, and splits into chunks
using a recursive strategy (chunk_size=300 chars, overlap=50 chars).
"""

import re
import pdfplumber
from pathlib import Path

DOCUMENTS_DIR = Path(__file__).parent / "documents"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

# Separators tried in order — section breaks first, then paragraphs, lines, words, chars
SEPARATORS = ["\n\n", "\n", " ", ""]

# PDF ligature glyphs -> plain ASCII. Covers both standard Unicode ligatures
# (U+FB00-FB06) and the Private Use Area codepoints observed in these syllabi.
_LIGATURES = {
    # Standard Unicode ligatures (U+FB00-FB06)
    "ﬀ": "ff",
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
    "ﬅ": "st",
    # PUA codepoints from raw extraction: ="ffi", ="fi", ="ffi"
    "": "ffi",
    "": "fi",
    "": "fl",
    "": "ffi",
    "": "ffl",
    "": "st",
}


def extract_text(pdf_path: Path) -> str:
    """Extract raw text from all pages of a PDF using pdfplumber."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n\n".join(pages)


def clean_text(text: str) -> str:
    """Remove common PDF artifacts and normalize whitespace."""
    # Replace known ligature glyphs with plain ASCII
    for glyph, replacement in _LIGATURES.items():
        text = text.replace(glyph, replacement)
    # Collapse runs of whitespace that aren't newlines
    text = re.sub(r"[^\S\n]+", " ", text)
    # Collapse 3+ consecutive newlines down to two (preserve paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove "Jump to a particular section:" navigation blocks (e.g. DST 490)
    text = re.sub(r"Jump to a particular section:[^\n]*\n(?:[^\n]+\n){1,3}", "", text)
    # Remove cover-page decoration: lines with digits but no letters
    # (Pascal's triangle rows, number sequences, garbled matrix notation)
    text = re.sub(r"(?m)^[^a-zA-Z\n]*\d[^a-zA-Z\n]*$", "", text)
    # Drop lines that are purely page numbers (e.g. "1", "- 2 -")
    text = re.sub(r"(?m)^[\s\-–—]*\d+[\s\-–—]*$", "", text)
    # Re-collapse any blank lines left behind
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def recursive_split(text: str, separators: list[str], chunk_size: int, overlap: int) -> list[str]:
    """
    Split text recursively: try each separator in order.
    When a piece still exceeds chunk_size, recurse with the next separator.
    Merge small pieces back up to chunk_size with overlap between consecutive chunks.
    """
    separator = separators[0]
    remaining = separators[1:]

    if separator:
        splits = text.split(separator)
    else:
        # Character-level fallback: slice directly
        chunks = []
        for start in range(0, len(text), chunk_size - overlap):
            chunks.append(text[start : start + chunk_size])
        return chunks

    good: list[str] = []
    for piece in splits:
        piece = piece.strip()
        if not piece:
            continue
        if len(piece) <= chunk_size:
            good.append(piece)
        elif remaining:
            good.extend(recursive_split(piece, remaining, chunk_size, overlap))
        else:
            # No more separators — slice by character
            for start in range(0, len(piece), chunk_size - overlap):
                good.append(piece[start : start + chunk_size])

    return merge_splits(good, separator, chunk_size, overlap)


def merge_splits(splits: list[str], separator: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Greedily merge split pieces into chunks up to chunk_size.
    Overlap is achieved by retaining whole pieces from the front of the
    completed chunk (popping until the remainder fits within `overlap` chars)
    so those pieces begin the next chunk — no raw-substring duplication.
    """
    chunks: list[str] = []
    current_parts: list[str] = []
    sep_len = len(separator)

    def total_len(parts: list[str]) -> int:
        return sum(len(p) for p in parts) + sep_len * max(len(parts) - 1, 0)

    for part in splits:
        if not part:
            continue
        add_len = total_len(current_parts) + (sep_len if current_parts else 0) + len(part)
        if add_len > chunk_size and current_parts:
            chunks.append(separator.join(current_parts))
            # Pop from the front until what remains fits within overlap
            while current_parts and total_len(current_parts) > overlap:
                current_parts.pop(0)
        current_parts.append(part)

    if current_parts:
        chunks.append(separator.join(current_parts))

    return chunks


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    return recursive_split(text, SEPARATORS, chunk_size, overlap)


def load_and_chunk_all() -> list[dict]:
    """
    Load every PDF in documents/, clean the text, and return a flat list of
    chunk dicts: {text, source, chunk_index}.
    """
    all_chunks: list[dict] = []

    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {DOCUMENTS_DIR}")
        return all_chunks

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        raw = extract_text(pdf_path)
        cleaned = clean_text(raw)
        chunks = chunk_text(cleaned)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": pdf_path.name,
                "chunk_index": i,
            })

        print(f"  -> {len(chunks)} chunks")

    print(f"\nTotal chunks across all documents: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    chunks = load_and_chunk_all()

    # Spot-check: print the first 3 chunks from each source
    seen: dict[str, int] = {}
    for chunk in chunks:
        src = chunk["source"]
        seen[src] = seen.get(src, 0) + 1
        if seen[src] <= 3:
            print(f"\n--- {src} | chunk {chunk['chunk_index']} ---")
            print(repr(chunk["text"]))

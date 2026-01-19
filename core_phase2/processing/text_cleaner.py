import re

def clean_ocr_text(raw_text: str) -> str:
    # Normalize line endings
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove repeated blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove non-informative OCR artifacts
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # Strip leading/trailing spaces per line
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines)

import os
from pathlib import Path
from typing import Iterator

SCHOOL_DIR = Path(os.getenv("SCHOOL_DIR", "./chef_knowledge_data")).expanduser()


def iter_school_files() -> Iterator[Path]:
    """Yield Path objects for files under the configured school directory."""
    for root, dirs, files in os.walk(SCHOOL_DIR):
        for f in files:
            path = Path(root) / f
            yield path


def read_docx(path: Path) -> str:
    try:
        import docx

        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""


def read_pdf(path: Path) -> str:
    try:
        import pdfplumber

        out: list[str] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                out.append(page.extract_text() or "")
        return "\n".join(out)
    except Exception:
        return ""


def read_odt(path: Path) -> str:
    try:
        from odf import text, teletype
        from odf.opendocument import load

        doc = load(str(path))
        out: list[str] = []
        for elem in doc.getElementsByType(text.P):
            out.append(teletype.extractText(elem))
        return "\n".join(out)
    except Exception:
        return ""


def extract_text(path: Path) -> str:
    """Extract readable text from supported file types; returns empty string if unsupported or on error."""
    ext = path.suffix.lower()
    if ext == ".docx":
        return read_docx(path)
    if ext == ".pdf":
        return read_pdf(path)
    if ext == ".odt":
        return read_odt(path)
    # fallback: try to read as plain text
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


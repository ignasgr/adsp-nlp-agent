from __future__ import annotations

import hashlib
from pathlib import Path

from pypdf import PdfReader


def stable_id(collection: str, source: str, page_number: int) -> str:
    raw = f"{collection}:{source}:{page_number}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()


def extract_pdf_pages(path: Path) -> list[tuple[int, str]]:
    reader = PdfReader(str(path))
    pages: list[tuple[int, str]] = []

    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append((i, text))

    return pages

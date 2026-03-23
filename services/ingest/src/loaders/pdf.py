from __future__ import annotations

from pathlib import Path

from .common import extract_pdf_pages
from .types import RawPage


def load_pdf_pages(source_dir: str) -> list[RawPage]:
    root = Path(source_dir)
    if not root.exists():
        return []

    pages: list[RawPage] = []
    for path in sorted(root.rglob("*.pdf")):
        if path.is_dir():
            continue

        source = str(path.relative_to(root.parent))
        for page_number, text in extract_pdf_pages(path):
            pages.append(
                RawPage(
                    text=text,
                    page_number=page_number,
                    source=source,
                    source_path=path,
                )
            )

    return pages

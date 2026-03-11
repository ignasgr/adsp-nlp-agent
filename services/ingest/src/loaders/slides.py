from __future__ import annotations

import re
from pathlib import Path

from .common import extract_pdf_pages, stable_id
from .types import IngestDocument


def _extract_lecture_number(path: Path) -> int:
    pattern = re.compile(r"(?:lecture|lec|week)[ _-]?(\d+)", flags=re.IGNORECASE)

    for token in [path.stem, *path.parts]:
        match = pattern.search(token)
        if match:
            return int(match.group(1))

    # 0 means "not detected" and is still filterable.
    return 0


def load_slide_documents(slides_dir: str, collection_name: str) -> list[IngestDocument]:
    root = Path(slides_dir)
    if not root.exists():
        return []

    docs: list[IngestDocument] = []
    for path in sorted(root.rglob("*.pdf")):
        if path.is_dir():
            continue

        source = str(path.relative_to(root.parent))
        lecture_number = _extract_lecture_number(path)

        for page_number, text in extract_pdf_pages(path):
            docs.append(
                IngestDocument(
                    id=stable_id(collection_name, source, page_number),
                    text=text,
                    metadata={
                        "source": source,
                        "lecture_number": lecture_number,
                        "page_number": page_number,
                    },
                )
            )

    return docs

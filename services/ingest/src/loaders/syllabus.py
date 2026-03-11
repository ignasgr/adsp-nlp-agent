from __future__ import annotations

from pathlib import Path

from .common import extract_pdf_pages, stable_id
from .types import IngestDocument


def load_syllabus_documents(syllabus_dir: str, collection_name: str) -> list[IngestDocument]:
    root = Path(syllabus_dir)
    if not root.exists():
        return []

    docs: list[IngestDocument] = []
    for path in sorted(root.rglob("*.pdf")):
        if path.is_dir():
            continue

        source = str(path.relative_to(root.parent))

        for page_number, text in extract_pdf_pages(path):
            docs.append(
                IngestDocument(
                    id=stable_id(collection_name, source, page_number),
                    text=text,
                    metadata={
                        "source": source,
                        "page_number": page_number,
                    },
                )
            )

    return docs

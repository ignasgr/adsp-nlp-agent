from __future__ import annotations

import re
from pathlib import Path

from ..loaders.common import stable_id
from ..loaders.types import IngestDocument, RawPage


def _extract_lecture_number(path: Path) -> int:
    pattern = re.compile(r"(?:lecture|lec|week)[ _-]?(\d+)", flags=re.IGNORECASE)
    for token in [path.stem, *path.parts]:
        match = pattern.search(token)
        if match:
            return int(match.group(1))
    return 0


def chunk(pages: list[RawPage], collection_name: str) -> list[IngestDocument]:
    return [
        IngestDocument(
            id=stable_id(collection_name, p.source, p.page_number),
            text=p.text,
            metadata={
                "source": p.source,
                "lecture_number": _extract_lecture_number(p.source_path),
                "page_number": p.page_number,
            },
        )
        for p in pages
    ]

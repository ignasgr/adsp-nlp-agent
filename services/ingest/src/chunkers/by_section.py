from __future__ import annotations

from ..loaders.common import stable_id
from ..loaders.types import IngestDocument, RawPage


def chunk(pages: list[RawPage], collection_name: str) -> list[IngestDocument]:
    return [
        IngestDocument(
            id=stable_id(collection_name, p.source, p.page_number),
            text=p.text,
            metadata={
                "source": p.source,
                "page_number": p.page_number,
            },
        )
        for p in pages
    ]

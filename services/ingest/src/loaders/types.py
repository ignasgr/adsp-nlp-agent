from dataclasses import dataclass
from pathlib import Path


@dataclass
class RawPage:
    text: str
    page_number: int
    source: str       # relative path string, used as metadata
    source_path: Path # absolute path, available to chunkers that need filename parsing


@dataclass
class IngestDocument:
    id: str
    text: str
    metadata: dict[str, int | str]

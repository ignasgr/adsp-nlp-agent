from dataclasses import dataclass


@dataclass
class IngestDocument:
    id: str
    text: str
    metadata: dict[str, int | str]

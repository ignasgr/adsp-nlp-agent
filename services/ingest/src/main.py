from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from .chunkers import get_chunker
from .config import get_settings
from .loaders import get_loader
from .vector_store import IngestVectorStore


@dataclass
class CollectionSpec:
    name: str
    source: str
    loader: str
    chunker: str


def load_collection_specs(config_path: str, data_root: str) -> list[CollectionSpec]:
    with open(config_path) as f:
        raw = yaml.safe_load(f)

    return [
        CollectionSpec(
            name=item["name"],
            source=str(Path(data_root) / item["source"]),
            loader=item["loader"],
            chunker=item["chunker"],
        )
        for item in raw["collections"]
    ]


def ingest_collection(store: IngestVectorStore, spec: CollectionSpec) -> dict[str, int]:
    pages = get_loader(spec.loader)(spec.source)
    documents = get_chunker(spec.chunker)(pages, spec.name)
    upserted = store.ingest_documents(spec.name, documents)
    return {"loaded_chunks": len(documents), "upserted_points": upserted}


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch ingestion job.")
    parser.add_argument(
        "--target",
        default="all",
        help="Collection name to ingest, or 'all'.",
    )
    args = parser.parse_args()

    settings = get_settings()
    store = IngestVectorStore(settings)
    specs = load_collection_specs(settings.collections_config, settings.data_root)

    if args.target != "all":
        specs = [s for s in specs if s.name == args.target]
        if not specs:
            raise ValueError(
                f"No collection named {args.target!r} in {settings.collections_config}"
            )

    results = {}
    for spec in specs:
        results[spec.name] = ingest_collection(store, spec)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

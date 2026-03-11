from __future__ import annotations

import argparse
import json

from .config import get_settings
from .loaders.slides import load_slide_documents
from .loaders.syllabus import load_syllabus_documents
from .vector_store import IngestVectorStore


def ingest_slides(store: IngestVectorStore, settings) -> dict[str, int]:
    documents = load_slide_documents(
        slides_dir=settings.slides_dir,
        collection_name=settings.chroma_slides_collection,
    )
    upserted = store.ingest_documents(settings.chroma_slides_collection, documents)
    return {"loaded_chunks": len(documents), "upserted_points": upserted}


def ingest_syllabus(store: IngestVectorStore, settings) -> dict[str, int]:
    documents = load_syllabus_documents(
        syllabus_dir=settings.syllabus_dir,
        collection_name=settings.chroma_syllabus_collection,
    )
    upserted = store.ingest_documents(settings.chroma_syllabus_collection, documents)
    return {"loaded_chunks": len(documents), "upserted_points": upserted}


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch ingestion job for slides/syllabus into Chroma.")
    parser.add_argument(
        "--target",
        choices=["all", "slides", "syllabus"],
        default="all",
        help="Select which collection to ingest.",
    )
    args = parser.parse_args()

    settings = get_settings()
    store = IngestVectorStore(settings)

    if args.target == "slides":
        result = {"slides": ingest_slides(store, settings)}
    elif args.target == "syllabus":
        result = {"syllabus": ingest_syllabus(store, settings)}
    else:
        slides = ingest_slides(store, settings)
        syllabus = ingest_syllabus(store, settings)
        result = {
            "all": {
                "slides_loaded_chunks": slides["loaded_chunks"],
                "slides_upserted_points": slides["upserted_points"],
                "syllabus_loaded_chunks": syllabus["loaded_chunks"],
                "syllabus_upserted_points": syllabus["upserted_points"],
            }
        }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

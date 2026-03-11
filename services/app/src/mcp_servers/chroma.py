import os
import sys
from typing import Any

import chromadb
from agents.mcp import MCPServerStdio
from fastmcp import FastMCP

CHROMA_DATA_DIR = os.getenv("CHROMA_DATA_DIR", "/workspace/chroma")

mcp = FastMCP("Local Chroma MCP")
client = chromadb.PersistentClient(path=CHROMA_DATA_DIR)


def _format_reference(metadata: dict[str, Any] | None) -> str:
    if not metadata:
        return ""

    source = metadata.get("source", "unknown source")
    lecture_number = metadata.get("lecture_number")
    page_number = metadata.get("page_number")

    parts = [str(source)]
    if lecture_number is not None:
        parts.append(f"lecture {lecture_number}")
    if page_number is not None:
        parts.append(f"slide {page_number}")

    return ", ".join(parts)


def create_chroma_mcp_server() -> MCPServerStdio:
    return MCPServerStdio(
        name="Chroma MCP",
        params={
            "command": sys.executable,
            "args": [
                "src/mcp_servers/chroma.py",
            ],
        },
        cache_tools_list=True,
    )


@mcp.tool
def list_collections() -> list[str]:
    """Return the names of all collections in the local persistent Chroma store.

    This is useful when the agent needs to discover which knowledge bases are
    currently available before choosing one to query.
    """
    collections = client.list_collections()
    return [collection.name for collection in collections]


@mcp.tool
def count_collections() -> int:
    """Return the total number of collections in the local Chroma store.

    This provides a lightweight way to confirm whether the database is empty or
    populated without retrieving the full collection list.
    """
    return client.count_collections()


@mcp.tool
def get_collection_schema(
    collection_name: str,
    sample_size: int = 5,
) -> dict[str, Any]:
    """Return the observed metadata schema for a collection.

    Args:
        collection_name: The exact Chroma collection name to inspect.
        sample_size: Number of sample records to inspect for metadata keys.

    Returns:
        A summary containing the collection name, observed metadata keys, and
        sample metadata records.

    Use this when the agent needs to learn which metadata fields are available
    before constructing filtered Chroma queries.
    """
    collection = client.get_collection(name=collection_name)
    sample = collection.get(limit=sample_size, include=["metadatas"])
    metadatas = sample.get("metadatas", []) or []

    metadata_keys = sorted(
        {key for metadata in metadatas if metadata for key in metadata.keys()}
    )

    return {
        "collection_name": collection_name,
        "metadata_keys": metadata_keys,
        "sample_metadatas": metadatas,
    }


@mcp.tool
def query_documents(
    collection_name: str,
    query_text: str,
    n_results: int = 5,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Query a collection and return compact, agent-friendly document matches.

    Args:
        collection_name: The exact Chroma collection name to search.
        query_text: The natural-language query to embed and search against.
        n_results: Maximum number of matches to return. Defaults to 5.
        where: Optional metadata filter applied by Chroma before returning
            matches. This should follow Chroma's metadata filter structure.

    Returns:
        A list of matches. Each match includes the stored record id, document
        text, metadata, and distance score returned by Chroma.

    Use this tool when the agent already knows which collection to search and
    needs relevant documents to answer a user question.
    """
    collection = client.get_collection(name=collection_name)
    result = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    ids = result.get("ids", [[]])[0]
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    matches = []
    for record_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        matches.append(
            {
                "id": record_id,
                "document": document,
                "metadata": metadata,
                "distance": distance,
                "reference": _format_reference(metadata),
            }
        )

    return matches


@mcp.tool
def get_slide_page(
    lecture_number: int,
    page_number: int,
    n_results: int = 3,
) -> list[dict[str, Any]]:
    """Retrieve slide chunks for a specific lecture and slide/page number.

    Args:
        lecture_number: The lecture number extracted during slide ingestion.
        page_number: The page number extracted from the slide PDF.
        n_results: Maximum number of matching chunks to return.

    Returns:
        Matching slide chunks from the `slides` collection, including document
        text, metadata, and distance score.

    Use this when a student asks about a specific slide from a known lecture,
    such as "slide 34 from week 5".
    """
    collection = client.get_collection(name="slides")
    result = collection.query(
        query_texts=[f"lecture {lecture_number} slide {page_number}"],
        n_results=n_results,
        where={
            "$and": [
                {"lecture_number": lecture_number},
                {"page_number": page_number},
            ]
        },
        include=["documents", "metadatas", "distances"],
    )

    ids = result.get("ids", [[]])[0]
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    matches = []
    for record_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        matches.append(
            {
                "id": record_id,
                "document": document,
                "metadata": metadata,
                "distance": distance,
                "reference": _format_reference(metadata),
            }
        )

    return matches


if __name__ == "__main__":
    mcp.run()

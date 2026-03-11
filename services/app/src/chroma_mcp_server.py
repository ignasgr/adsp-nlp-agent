import os
from typing import Any

import chromadb
from fastmcp import FastMCP

CHROMA_DATA_DIR = os.getenv("CHROMA_DATA_DIR", "/workspace/chroma")

mcp = FastMCP("Local Chroma MCP")
client = chromadb.PersistentClient(path=CHROMA_DATA_DIR)


@mcp.tool
def chroma_list_collections() -> list[str]:
    """Return the names of all collections in the local persistent Chroma store.

    This is useful when the agent needs to discover which knowledge bases are
    currently available before choosing one to query.
    """
    collections = client.list_collections()
    return [collection.name for collection in collections]


@mcp.tool
def chroma_get_collection_count() -> int:
    """Return the total number of collections in the local Chroma store.

    This provides a lightweight way to confirm whether the database is empty or
    populated without retrieving the full collection list.
    """
    return client.count_collections()


@mcp.tool
def chroma_query_documents(
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
            }
        )

    return matches


if __name__ == "__main__":
    mcp.run()

from __future__ import annotations

import chromadb
from sentence_transformers import SentenceTransformer

from .config import Settings
from .loaders.types import IngestDocument


class IngestVectorStore:
    def __init__(self, settings: Settings) -> None:
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
        )
        self.settings = settings
        self.embedding_model = SentenceTransformer(settings.embedding_model)

    def _create_collection(self, collection_name: str):
        hnsw_cfg = {
            "space": self.settings.chroma_hnsw_space,
            "max_neighbors": self.settings.chroma_hnsw_m,
            "ef_construction": self.settings.chroma_hnsw_construction_ef,
            "ef_search": self.settings.chroma_hnsw_search_ef,
        }
        try:
            self.client.delete_collection(name=collection_name)
        except Exception:
            # First run or missing collection.
            pass

        return self.client.create_collection(
            name=collection_name,
            configuration={"hnsw": hnsw_cfg},
        )

    def ingest_documents(
        self, collection_name: str, documents: list[IngestDocument]
    ) -> int:
        collection = self._create_collection(collection_name)
        if not documents:
            return 0

        texts = [doc.text for doc in documents]
        ids = [doc.id for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        embeddings = self.embedding_model.encode(
            texts, normalize_embeddings=True
        ).tolist()

        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return len(ids)

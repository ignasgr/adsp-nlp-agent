from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    chroma_persist_directory: str = Field(
        default="/workspace/chroma",
        alias="CHROMA_PERSIST_DIRECTORY",
    )
    chroma_slides_collection: str = Field(default="slides", alias="CHROMA_SLIDES_COLLECTION")
    chroma_syllabus_collection: str = Field(default="syllabus", alias="CHROMA_SYLLABUS_COLLECTION")
    chroma_hnsw_space: str = Field(default="cosine", alias="CHROMA_HNSW_SPACE")
    chroma_hnsw_m: int = Field(default=16, alias="CHROMA_HNSW_M")
    chroma_hnsw_construction_ef: int = Field(default=100, alias="CHROMA_HNSW_CONSTRUCTION_EF")
    chroma_hnsw_search_ef: int = Field(default=100, alias="CHROMA_HNSW_SEARCH_EF")
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )

    slides_dir: str = Field(default="/workspace/data/slides", alias="SLIDES_DIR")
    syllabus_dir: str = Field(default="/workspace/data/syllabus", alias="SYLLABUS_DIR")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

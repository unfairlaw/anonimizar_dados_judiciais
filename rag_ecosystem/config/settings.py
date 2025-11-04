"""Configuration settings for the RAG Ecosystem."""

from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Global configuration settings for the RAG ecosystem."""

    # LLM Configuration
    llm_provider: Literal["openai", "anthropic", "ollama"] = "openai"
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 2048

    # Embedding Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # Vector Store Configuration
    vector_store_type: Literal["chroma", "faiss"] = "chroma"
    vector_store_path: str = "./data/vector_store"
    collection_name: str = "rag_documents"

    # Retrieval Configuration
    retrieval_top_k: int = 5
    retrieval_method: Literal["vector", "keyword", "hybrid"] = "hybrid"
    hybrid_alpha: float = 0.5  # Weight for vector vs keyword search

    # Reranking Configuration
    reranking_enabled: bool = True
    reranking_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranking_top_k: int = 3

    # Query Transformation
    query_rewriting_enabled: bool = True
    max_query_rewrites: int = 2

    # Routing Configuration
    routing_enabled: bool = True
    enable_web_search: bool = False

    # Agentic RAG Configuration
    self_correction_enabled: bool = True
    max_correction_iterations: int = 3
    relevance_threshold: float = 0.7

    # Evaluation Configuration
    evaluation_metrics: list[str] = Field(
        default_factory=lambda: [
            "context_relevancy",
            "answer_relevancy",
            "faithfulness",
            "context_recall"
        ]
    )

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_file: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

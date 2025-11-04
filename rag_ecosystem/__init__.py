"""
RAG Ecosystem - A comprehensive implementation of a production-ready RAG system.

This package includes:
- Query Transformations: Query rewriting and optimization
- Intelligent Routing: Dynamic query routing to appropriate data sources
- Advanced Indexing: Multi-layered knowledge bases with embeddings
- Retrieval & Re-ranking: Vector search with cross-encoder reranking
- Self-Correcting Agentic Flows: Document grading and response validation
- End-to-End Evaluation: Comprehensive pipeline metrics
"""

__version__ = "1.0.0"
__author__ = "RAG Ecosystem Team"

from rag_ecosystem.config.settings import Settings

__all__ = ["Settings"]

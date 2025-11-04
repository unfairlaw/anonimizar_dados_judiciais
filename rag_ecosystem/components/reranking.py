"""Document reranking module using cross-encoders."""

from typing import List, Optional
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from rag_ecosystem.config.settings import get_settings


class DocumentReranker:
    """Reranks retrieved documents using cross-encoder models."""

    def __init__(self, model_name: Optional[str] = None):
        """Initialize the document reranker.

        Args:
            model_name: Cross-encoder model name (optional)
        """
        self.settings = get_settings()
        self.model_name = model_name or self.settings.reranking_model
        self.model = self._initialize_model()

    def _initialize_model(self) -> CrossEncoder:
        """Initialize the cross-encoder model."""
        return CrossEncoder(self.model_name)

    def rerank(self, query: str, documents: List[Document],
              top_k: Optional[int] = None) -> List[Document]:
        """Rerank documents based on relevance to query.

        Args:
            query: Search query
            documents: List of documents to rerank
            top_k: Number of top documents to return

        Returns:
            Reranked list of documents
        """
        if not documents:
            return documents

        if top_k is None:
            top_k = self.settings.reranking_top_k

        # Prepare query-document pairs
        pairs = [[query, doc.page_content] for doc in documents]

        # Get relevance scores from cross-encoder
        scores = self.model.predict(pairs)

        # Attach scores to documents
        for doc, score in zip(documents, scores):
            doc.metadata['reranking_score'] = float(score)
            # Preserve original retrieval score
            doc.metadata['original_score'] = doc.metadata.get('retrieval_score', 0)

        # Sort by reranking score
        reranked_docs = sorted(documents,
                              key=lambda d: d.metadata['reranking_score'],
                              reverse=True)

        # Return top-k
        return reranked_docs[:top_k]

    def get_relevance_score(self, query: str, document: Document) -> float:
        """Get relevance score for a single query-document pair.

        Args:
            query: Search query
            document: Document to score

        Returns:
            Relevance score
        """
        score = self.model.predict([[query, document.page_content]])
        return float(score[0])

    def filter_by_threshold(self, query: str, documents: List[Document],
                           threshold: Optional[float] = None) -> List[Document]:
        """Filter documents by minimum relevance threshold.

        Args:
            query: Search query
            documents: List of documents to filter
            threshold: Minimum relevance score (uses settings if None)

        Returns:
            Filtered list of documents
        """
        if threshold is None:
            threshold = self.settings.relevance_threshold

        reranked = self.rerank(query, documents, top_k=len(documents))

        return [doc for doc in reranked
                if doc.metadata.get('reranking_score', 0) >= threshold]

"""Document retrieval module with multiple retrieval strategies."""

from typing import List, Optional, Dict, Any, Literal
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
import chromadb
from chromadb.config import Settings as ChromaSettings
from rag_ecosystem.config.settings import get_settings
from rag_ecosystem.utils.llm_factory import create_embeddings


class DocumentRetriever:
    """Retrieves relevant documents using various strategies."""

    def __init__(self, embedding_model: Optional[Any] = None):
        """Initialize the document retriever.

        Args:
            embedding_model: Custom embedding model (optional)
        """
        self.settings = get_settings()
        self.embeddings = embedding_model or self._initialize_embeddings()
        self.vector_store = self._initialize_vector_store()
        self.bm25_index = None
        self.bm25_documents = []

    def _initialize_embeddings(self):
        """Initialize the embedding model."""
        return create_embeddings()
    def _initialize_vector_store(self):
        """Initialize connection to the vector store."""
        if self.settings.vector_store_type == "chroma":
            client = chromadb.PersistentClient(
                path=self.settings.vector_store_path,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            return client.get_or_create_collection(
                name=self.settings.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        else:
            raise NotImplementedError(
                f"Vector store {self.settings.vector_store_type} not implemented"
            )

    def _build_bm25_index(self) -> None:
        """Build BM25 index from vector store documents."""
        # Get all documents from vector store
        results = self.vector_store.get()

        if not results['documents']:
            return

        # Store documents
        self.bm25_documents = [
            Document(
                page_content=doc,
                metadata=meta or {}
            )
            for doc, meta in zip(results['documents'], results['metadatas'])
        ]

        # Tokenize documents for BM25
        tokenized_docs = [doc.page_content.lower().split()
                         for doc in self.bm25_documents]

        # Build BM25 index
        self.bm25_index = BM25Okapi(tokenized_docs)

    def retrieve_vector(self, query: str, top_k: Optional[int] = None) -> List[Document]:
        """Retrieve documents using vector similarity search.

        Args:
            query: Search query
            top_k: Number of documents to retrieve

        Returns:
            List of retrieved documents
        """
        if top_k is None:
            top_k = self.settings.retrieval_top_k

        # Embed the query
        query_embedding = self.embeddings.embed_query(query)

        # Query vector store
        results = self.vector_store.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Convert to Document objects
        documents = []
        if results['documents'] and results['documents'][0]:
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                metadata = metadata or {}
                metadata['retrieval_score'] = 1 - distance  # Convert distance to similarity
                metadata['retrieval_method'] = 'vector'

                documents.append(Document(
                    page_content=doc,
                    metadata=metadata
                ))

        return documents

    def retrieve_keyword(self, query: str, top_k: Optional[int] = None) -> List[Document]:
        """Retrieve documents using BM25 keyword search.

        Args:
            query: Search query
            top_k: Number of documents to retrieve

        Returns:
            List of retrieved documents
        """
        if top_k is None:
            top_k = self.settings.retrieval_top_k

        # Build BM25 index if not already built
        if self.bm25_index is None:
            self._build_bm25_index()

        if not self.bm25_documents:
            return []

        # Tokenize query
        tokenized_query = query.lower().split()

        # Get BM25 scores
        scores = self.bm25_index.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        # Create documents with scores
        documents = []
        for idx in top_indices:
            doc = self.bm25_documents[idx]
            doc.metadata['retrieval_score'] = float(scores[idx])
            doc.metadata['retrieval_method'] = 'keyword'
            documents.append(doc)

        return documents

    def retrieve_hybrid(self, query: str, top_k: Optional[int] = None,
                       alpha: Optional[float] = None) -> List[Document]:
        """Retrieve documents using hybrid vector + keyword search.

        Args:
            query: Search query
            top_k: Number of documents to retrieve
            alpha: Weight for vector search (1-alpha for keyword). Default from settings.

        Returns:
            List of retrieved documents
        """
        if top_k is None:
            top_k = self.settings.retrieval_top_k

        if alpha is None:
            alpha = self.settings.hybrid_alpha

        # Get results from both methods
        vector_docs = self.retrieve_vector(query, top_k * 2)
        keyword_docs = self.retrieve_keyword(query, top_k * 2)

        # Create a combined scoring dictionary
        doc_scores: Dict[str, Dict[str, Any]] = {}

        # Add vector search results
        for doc in vector_docs:
            doc_id = doc.page_content
            doc_scores[doc_id] = {
                'document': doc,
                'vector_score': doc.metadata.get('retrieval_score', 0),
                'keyword_score': 0
            }

        # Add keyword search results
        for doc in keyword_docs:
            doc_id = doc.page_content
            if doc_id in doc_scores:
                doc_scores[doc_id]['keyword_score'] = doc.metadata.get('retrieval_score', 0)
            else:
                doc_scores[doc_id] = {
                    'document': doc,
                    'vector_score': 0,
                    'keyword_score': doc.metadata.get('retrieval_score', 0)
                }

        # Normalize scores and compute hybrid score
        if doc_scores:
            max_vector = max(item['vector_score'] for item in doc_scores.values())
            max_keyword = max(item['keyword_score'] for item in doc_scores.values())

            for item in doc_scores.values():
                # Normalize scores
                norm_vector = item['vector_score'] / max_vector if max_vector > 0 else 0
                norm_keyword = item['keyword_score'] / max_keyword if max_keyword > 0 else 0

                # Compute hybrid score
                item['hybrid_score'] = alpha * norm_vector + (1 - alpha) * norm_keyword

        # Sort by hybrid score and get top-k
        sorted_docs = sorted(doc_scores.values(),
                           key=lambda x: x['hybrid_score'],
                           reverse=True)[:top_k]

        # Update metadata and return documents
        result_docs = []
        for item in sorted_docs:
            doc = item['document']
            doc.metadata['retrieval_score'] = item['hybrid_score']
            doc.metadata['retrieval_method'] = 'hybrid'
            doc.metadata['vector_score'] = item['vector_score']
            doc.metadata['keyword_score'] = item['keyword_score']
            result_docs.append(doc)

        return result_docs

    def retrieve(self, query: str,
                method: Optional[Literal["vector", "keyword", "hybrid"]] = None,
                top_k: Optional[int] = None) -> List[Document]:
        """Main retrieval method that uses configured strategy.

        Args:
            query: Search query
            method: Retrieval method (overrides settings)
            top_k: Number of documents to retrieve

        Returns:
            List of retrieved documents
        """
        if method is None:
            method = self.settings.retrieval_method

        if method == "vector":
            return self.retrieve_vector(query, top_k)
        elif method == "keyword":
            return self.retrieve_keyword(query, top_k)
        elif method == "hybrid":
            return self.retrieve_hybrid(query, top_k)
        else:
            raise ValueError(f"Unknown retrieval method: {method}")

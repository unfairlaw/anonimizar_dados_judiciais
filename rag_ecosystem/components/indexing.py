"""Document indexing and embedding module."""

from typing import List, Optional, Dict, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from rag_ecosystem.config.settings import get_settings
from rag_ecosystem.utils.llm_factory import create_embeddings


class DocumentIndexer:
    """Handles document indexing, chunking, and embedding."""

    def __init__(self, embedding_model: Optional[Any] = None):
        """Initialize the document indexer.

        Args:
            embedding_model: Custom embedding model (optional)
        """
        self.settings = get_settings()
        self.embeddings = embedding_model or self._initialize_embeddings()
        self.text_splitter = self._initialize_text_splitter()
        self.vector_store = self._initialize_vector_store()

    def _initialize_embeddings(self):
        """Initialize the embedding model."""
        return create_embeddings()
    def _initialize_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """Initialize the text splitter for chunking documents."""
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def _initialize_vector_store(self):
        """Initialize the vector store based on configuration."""
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

    def chunk_document(self, text: str, metadata: Optional[Dict] = None) -> List[Document]:
        """Split a document into chunks.

        Args:
            text: Document text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of document chunks
        """
        chunks = self.text_splitter.split_text(text)
        documents = []

        for i, chunk in enumerate(chunks):
            doc_metadata = metadata.copy() if metadata else {}
            doc_metadata["chunk_id"] = i
            doc_metadata["total_chunks"] = len(chunks)

            documents.append(Document(
                page_content=chunk,
                metadata=doc_metadata
            ))

        return documents

    def embed_documents(self, documents: List[Document]) -> List[List[float]]:
        """Generate embeddings for documents.

        Args:
            documents: List of documents to embed

        Returns:
            List of embedding vectors
        """
        texts = [doc.page_content for doc in documents]
        return self.embeddings.embed_documents(texts)

    def index_documents(self, documents: List[Document]) -> None:
        """Index documents into the vector store.

        Args:
            documents: List of documents to index
        """
        if not documents:
            return

        # Generate embeddings
        embeddings = self.embed_documents(documents)

        # Prepare data for ChromaDB
        ids = [f"doc_{i}_{doc.metadata.get('chunk_id', 0)}"
               for i, doc in enumerate(documents)]
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        # Add to vector store
        self.vector_store.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def index_from_text(self, text: str, metadata: Optional[Dict] = None) -> int:
        """Index a text document.

        Args:
            text: Document text
            metadata: Optional metadata

        Returns:
            Number of chunks indexed
        """
        documents = self.chunk_document(text, metadata)
        self.index_documents(documents)
        return len(documents)

    def index_from_file(self, file_path: str) -> int:
        """Index a document from a file.

        Args:
            file_path: Path to the file

        Returns:
            Number of chunks indexed
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content
        text = path.read_text(encoding='utf-8')

        metadata = {
            "source": str(path),
            "filename": path.name,
            "file_type": path.suffix
        }

        return self.index_from_text(text, metadata)

    def index_from_directory(self, directory_path: str,
                            file_pattern: str = "*.txt") -> int:
        """Index all matching files in a directory.

        Args:
            directory_path: Path to directory
            file_pattern: Glob pattern for files to index

        Returns:
            Total number of chunks indexed
        """
        directory = Path(directory_path)
        total_chunks = 0

        for file_path in directory.glob(file_pattern):
            if file_path.is_file():
                chunks = self.index_from_file(str(file_path))
                total_chunks += chunks

        return total_chunks

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed collection.

        Returns:
            Dictionary with collection statistics
        """
        count = self.vector_store.count()

        return {
            "total_documents": count,
            "collection_name": self.settings.collection_name,
            "embedding_model": self.settings.embedding_model,
            "vector_store_type": self.settings.vector_store_type
        }

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        # Get all IDs and delete
        results = self.vector_store.get()
        if results['ids']:
            self.vector_store.delete(ids=results['ids'])

"""Basic RAG example - Simple retrieval and generation."""

from rag_ecosystem.components.indexing import DocumentIndexer
from rag_ecosystem.components.retrieval import DocumentRetriever
from rag_ecosystem.components.generation import ResponseGenerator
from rag_ecosystem.utils.logger import setup_logger


def main():
    """Run a basic RAG example."""
    logger = setup_logger("basic_rag")

    # Sample documents
    documents = [
        "Python is a high-level programming language known for its simplicity and readability.",
        "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
        "Natural language processing (NLP) deals with the interaction between computers and human language.",
        "Deep learning uses neural networks with multiple layers to model complex patterns in data.",
        "The transformer architecture revolutionized NLP with its attention mechanism."
    ]

    logger.info("Starting Basic RAG Example")

    # Step 1: Index documents
    logger.info("Indexing documents...")
    indexer = DocumentIndexer()
    indexer.clear_collection()  # Start fresh

    for i, doc in enumerate(documents):
        indexer.index_from_text(doc, metadata={"doc_id": i, "source": "example"})

    logger.info(f"Indexed {len(documents)} documents")

    # Step 2: Retrieve relevant documents
    logger.info("\nRetrieving documents...")
    retriever = DocumentRetriever()

    query = "What is machine learning?"
    logger.info(f"Query: {query}")

    # Try different retrieval methods
    for method in ["vector", "keyword", "hybrid"]:
        logger.info(f"\nRetrieval method: {method}")
        docs = retriever.retrieve(query, method=method, top_k=3)

        for i, doc in enumerate(docs, 1):
            score = doc.metadata.get('retrieval_score', 0)
            logger.info(f"  {i}. [Score: {score:.3f}] {doc.page_content[:100]}...")

    # Step 3: Generate response
    logger.info("\nGenerating response...")
    generator = ResponseGenerator()

    retrieved_docs = retriever.retrieve(query, method="hybrid", top_k=3)
    response = generator.generate(query, retrieved_docs)

    logger.info(f"\nQuery: {query}")
    logger.info(f"Answer: {response}")

    # Get response with metadata
    response_with_meta = generator.generate_with_metadata(query, retrieved_docs)
    logger.info(f"\nMetadata:")
    logger.info(f"  Sources: {response_with_meta['sources']}")
    logger.info(f"  Documents used: {response_with_meta['num_documents_used']}")
    logger.info(f"  Avg relevance: {response_with_meta['average_relevance']:.3f}")


if __name__ == "__main__":
    main()

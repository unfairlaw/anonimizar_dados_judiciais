"""Agentic RAG example with self-correction."""

from rag_ecosystem.agents.agentic_rag import AgenticRAG
from rag_ecosystem.components.indexing import DocumentIndexer
from rag_ecosystem.utils.logger import setup_logger
import json


def main():
    """Run an agentic RAG example with self-correction."""
    logger = setup_logger("agentic_rag")

    # Sample knowledge base
    documents = [
        """The Retrieval-Augmented Generation (RAG) architecture combines the power of
        large language models with external knowledge retrieval. It consists of two main
        components: a retriever that fetches relevant documents from a knowledge base,
        and a generator that produces responses based on the retrieved context.""",

        """Self-correcting RAG systems can evaluate their own performance and iterate
        on poor results. They use document grading to filter irrelevant retrieved content
        and response evaluation to detect hallucinations or low-quality answers. If the
        initial attempt fails quality checks, the system can rewrite the query and retry.""",

        """Query routing is an intelligent decision-making process where queries are
        directed to the most appropriate data source. A query might go to a vector
        database for internal knowledge, web search for current information, or directly
        to the LLM for general knowledge questions.""",

        """Reranking improves retrieval quality by re-scoring initially retrieved documents
        using more sophisticated cross-encoder models. While initial retrieval uses
        efficient bi-encoders, reranking applies computationally expensive but more
        accurate models to the top candidates.""",

        """Multi-hop retrieval involves breaking down complex queries into simpler
        sub-queries that are executed sequentially. Each sub-query retrieves information
        that helps answer the next query, building up comprehensive context for complex
        questions that require multiple pieces of information."""
    ]

    logger.info("Starting Agentic RAG Example")

    # Step 1: Index documents
    logger.info("\nIndexing documents...")
    indexer = DocumentIndexer()
    indexer.clear_collection()

    for i, doc in enumerate(documents):
        indexer.index_from_text(doc, metadata={
            "doc_id": i,
            "source": "rag_knowledge_base",
            "topic": ["rag", "ai", "nlp"]
        })

    stats = indexer.get_collection_stats()
    logger.info(f"Collection stats: {json.dumps(stats, indent=2)}")

    # Step 2: Create Agentic RAG system
    logger.info("\nInitializing Agentic RAG system...")
    rag = AgenticRAG()

    # Test queries
    queries = [
        "What is RAG?",
        "How does self-correction work in RAG?",
        "Explain query routing and reranking",  # Multi-hop query
    ]

    for query in queries:
        logger.info("\n" + "="*70)
        logger.info(f"Query: {query}")
        logger.info("="*70)

        # Execute query with self-correction
        result = rag.query(query, enable_self_correction=True)

        logger.info(f"\nStatus: {result['status']}")
        logger.info(f"Answer:\n{result['answer']}")

        if result.get('documents'):
            logger.info(f"\nDocuments used: {len(result['documents'])}")

        if result.get('attempts'):
            logger.info(f"Attempts: {result['attempts']}")

        if result.get('evaluation'):
            eval_data = result['evaluation']
            logger.info(f"\nEvaluation:")
            logger.info(f"  Overall verdict: {eval_data['overall_verdict']}")
            if 'quality' in eval_data:
                logger.info(f"  Quality scores: {eval_data['quality']['scores']}")

    # Test multi-hop query
    logger.info("\n" + "="*70)
    logger.info("Multi-Hop Query Example")
    logger.info("="*70)

    complex_query = "What are the main components of RAG and how do they improve quality?"
    result = rag.multi_hop_query(complex_query)

    logger.info(f"\nComplex Query: {complex_query}")
    logger.info(f"\nSub-queries executed:")
    for i, sub_result in enumerate(result['sub_queries'], 1):
        logger.info(f"  {i}. {sub_result['sub_query']}")

    logger.info(f"\nFinal Answer:\n{result['answer']}")


if __name__ == "__main__":
    main()

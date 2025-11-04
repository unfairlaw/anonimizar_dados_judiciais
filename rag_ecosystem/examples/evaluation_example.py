"""Evaluation pipeline example."""

from rag_ecosystem.agents.agentic_rag import AgenticRAG
from rag_ecosystem.components.indexing import DocumentIndexer
from rag_ecosystem.evaluation.pipeline_evaluator import PipelineEvaluator, EvaluationCase
from rag_ecosystem.utils.logger import setup_logger


def main():
    """Run an evaluation pipeline example."""
    logger = setup_logger("evaluation")

    logger.info("Starting Evaluation Pipeline Example")

    # Index sample documents
    logger.info("\nIndexing documents...")
    indexer = DocumentIndexer()
    indexer.clear_collection()

    documents = [
        "Artificial Intelligence (AI) is the simulation of human intelligence in machines.",
        "Machine Learning is a subset of AI that enables systems to learn from data.",
        "Deep Learning uses neural networks with multiple layers.",
        "Natural Language Processing focuses on human-computer language interaction.",
        "Computer Vision enables machines to interpret visual information from the world."
    ]

    for i, doc in enumerate(documents):
        indexer.index_from_text(doc, metadata={"doc_id": i})

    logger.info(f"Indexed {len(documents)} documents")

    # Create RAG system
    rag = AgenticRAG()

    # Define test cases
    test_cases = [
        EvaluationCase(
            query="What is artificial intelligence?",
            expected_answer="AI is the simulation of human intelligence in machines",
            expected_topics=["ai", "machine learning"],
            metadata={"difficulty": "easy"}
        ),
        EvaluationCase(
            query="How is machine learning related to AI?",
            expected_answer="Machine learning is a subset of AI that learns from data",
            expected_topics=["ai", "machine learning"],
            metadata={"difficulty": "medium"}
        ),
        EvaluationCase(
            query="What are the applications of deep learning?",
            expected_answer=None,  # No ground truth
            expected_topics=["deep learning", "neural networks"],
            metadata={"difficulty": "hard"}
        ),
    ]

    # Run evaluation
    logger.info("\nRunning evaluation...")
    evaluator = PipelineEvaluator(rag)

    results = evaluator.evaluate_batch(test_cases)

    # Display results
    logger.info("\n" + "="*70)
    logger.info("EVALUATION RESULTS")
    logger.info("="*70)

    logger.info(f"\nTotal test cases: {results['total_cases']}")
    logger.info(f"Success rate: {results['success_rate']:.2%}")

    logger.info("\nMetrics Summary:")
    for metric_name, stats in results['metrics'].items():
        logger.info(f"  {metric_name}:")
        logger.info(f"    Mean: {stats['mean']:.3f}")
        logger.info(f"    Range: [{stats['min']:.3f}, {stats['max']:.3f}]")

    logger.info("\nPerformance:")
    perf = results['performance']
    logger.info(f"  Mean latency: {perf['mean_latency_ms']:.2f} ms")
    logger.info(f"  Median latency: {perf['median_latency_ms']:.2f} ms")

    # Generate and display full report
    logger.info("\n" + "="*70)
    logger.info("DETAILED REPORT")
    logger.info("="*70)
    print(evaluator.generate_report())

    # Save results
    output_path = "./data/evaluation_results.json"
    evaluator.save_results(output_path)
    logger.info(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()

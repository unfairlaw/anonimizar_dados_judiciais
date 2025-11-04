"""End-to-end RAG pipeline evaluation."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from rag_ecosystem.evaluation.metrics import RAGMetrics
from rag_ecosystem.agents.agentic_rag import AgenticRAG


@dataclass
class EvaluationCase:
    """Represents a single evaluation test case."""
    query: str
    expected_answer: Optional[str] = None
    expected_topics: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class PipelineEvaluator:
    """Evaluates the entire RAG pipeline end-to-end."""

    def __init__(self, rag_system: AgenticRAG):
        """Initialize the pipeline evaluator.

        Args:
            rag_system: Agentic RAG system to evaluate
        """
        self.rag_system = rag_system
        self.metrics_calculator = RAGMetrics()
        self.results: List[Dict[str, Any]] = []

    def evaluate_single(self, test_case: EvaluationCase) -> Dict[str, Any]:
        """Evaluate a single test case.

        Args:
            test_case: Test case to evaluate

        Returns:
            Evaluation results
        """
        # Execute query
        start_time = datetime.now()
        result = self.rag_system.query(test_case.query)
        end_time = datetime.now()

        # Calculate metrics
        metrics = self.metrics_calculator.compute_all_metrics(
            query=test_case.query,
            answer=result.get("answer", ""),
            documents=result.get("documents", []),
            ground_truth=test_case.expected_answer
        )

        # Compile results
        evaluation_result = {
            "test_case": {
                "query": test_case.query,
                "expected_answer": test_case.expected_answer,
                "expected_topics": test_case.expected_topics,
            },
            "result": {
                "status": result.get("status"),
                "answer": result.get("answer"),
                "num_documents": len(result.get("documents", [])),
                "attempts": result.get("attempts", 1),
            },
            "metrics": metrics,
            "performance": {
                "latency_ms": (end_time - start_time).total_seconds() * 1000,
                "timestamp": start_time.isoformat(),
            },
            "metadata": test_case.metadata or {}
        }

        self.results.append(evaluation_result)
        return evaluation_result

    def evaluate_batch(self, test_cases: List[EvaluationCase]) -> Dict[str, Any]:
        """Evaluate multiple test cases.

        Args:
            test_cases: List of test cases

        Returns:
            Aggregated evaluation results
        """
        self.results = []

        for test_case in test_cases:
            self.evaluate_single(test_case)

        return self.aggregate_results()

    def aggregate_results(self) -> Dict[str, Any]:
        """Aggregate results from all evaluations.

        Returns:
            Aggregated statistics
        """
        if not self.results:
            return {"error": "No results to aggregate"}

        # Aggregate metrics
        metric_names = list(self.results[0]["metrics"].keys())
        aggregated_metrics = {}

        for metric_name in metric_names:
            values = [r["metrics"][metric_name] for r in self.results]
            aggregated_metrics[metric_name] = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "median": sorted(values)[len(values) // 2],
            }

        # Aggregate performance
        latencies = [r["performance"]["latency_ms"] for r in self.results]
        performance_stats = {
            "mean_latency_ms": sum(latencies) / len(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "median_latency_ms": sorted(latencies)[len(latencies) // 2],
        }

        # Status distribution
        statuses = [r["result"]["status"] for r in self.results]
        status_counts = {}
        for status in set(statuses):
            status_counts[status] = statuses.count(status)

        return {
            "total_cases": len(self.results),
            "metrics": aggregated_metrics,
            "performance": performance_stats,
            "status_distribution": status_counts,
            "success_rate": status_counts.get("success", 0) / len(self.results),
            "timestamp": datetime.now().isoformat(),
        }

    def save_results(self, output_path: str) -> None:
        """Save evaluation results to a file.

        Args:
            output_path: Path to save results
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "individual_results": self.results,
            "aggregated_results": self.aggregate_results()
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_report(self) -> str:
        """Generate a human-readable evaluation report.

        Returns:
            Formatted report string
        """
        if not self.results:
            return "No evaluation results available."

        agg = self.aggregate_results()

        report = []
        report.append("=" * 60)
        report.append("RAG PIPELINE EVALUATION REPORT")
        report.append("=" * 60)
        report.append(f"\nTotal Test Cases: {agg['total_cases']}")
        report.append(f"Success Rate: {agg['success_rate']:.2%}")
        report.append(f"\nTimestamp: {agg['timestamp']}")

        report.append("\n" + "=" * 60)
        report.append("METRICS")
        report.append("=" * 60)

        for metric_name, stats in agg['metrics'].items():
            report.append(f"\n{metric_name.replace('_', ' ').title()}:")
            report.append(f"  Mean:   {stats['mean']:.3f}")
            report.append(f"  Median: {stats['median']:.3f}")
            report.append(f"  Range:  [{stats['min']:.3f}, {stats['max']:.3f}]")

        report.append("\n" + "=" * 60)
        report.append("PERFORMANCE")
        report.append("=" * 60)

        perf = agg['performance']
        report.append(f"\nMean Latency:   {perf['mean_latency_ms']:.2f} ms")
        report.append(f"Median Latency: {perf['median_latency_ms']:.2f} ms")
        report.append(f"Range:          [{perf['min_latency_ms']:.2f}, {perf['max_latency_ms']:.2f}] ms")

        report.append("\n" + "=" * 60)
        report.append("STATUS DISTRIBUTION")
        report.append("=" * 60)

        for status, count in agg['status_distribution'].items():
            percentage = (count / agg['total_cases']) * 100
            report.append(f"\n{status}: {count} ({percentage:.1f}%)")

        report.append("\n" + "=" * 60)

        return "\n".join(report)

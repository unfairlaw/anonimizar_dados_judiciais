"""Evaluation metrics for RAG systems."""

from typing import List, Dict, Any
from langchain_core.documents import Document
import re


class RAGMetrics:
    """Computes various evaluation metrics for RAG systems."""

    @staticmethod
    def context_relevancy(query: str, documents: List[Document]) -> float:
        """Calculate context relevancy score.

        Measures how relevant the retrieved documents are to the query.

        Args:
            query: User query
            documents: Retrieved documents

        Returns:
            Relevancy score between 0 and 1
        """
        if not documents:
            return 0.0

        # Simple keyword-based relevancy (can be enhanced with embeddings)
        query_terms = set(query.lower().split())

        relevancy_scores = []
        for doc in documents:
            doc_terms = set(doc.page_content.lower().split())
            overlap = len(query_terms.intersection(doc_terms))
            score = overlap / len(query_terms) if query_terms else 0
            relevancy_scores.append(score)

        return sum(relevancy_scores) / len(relevancy_scores)

    @staticmethod
    def answer_relevancy(query: str, answer: str) -> float:
        """Calculate answer relevancy to the query.

        Args:
            query: User query
            answer: Generated answer

        Returns:
            Relevancy score between 0 and 1
        """
        if not answer:
            return 0.0

        query_terms = set(query.lower().split())
        answer_terms = set(answer.lower().split())

        overlap = len(query_terms.intersection(answer_terms))
        score = overlap / len(query_terms) if query_terms else 0

        return min(score, 1.0)

    @staticmethod
    def faithfulness(answer: str, documents: List[Document]) -> float:
        """Calculate faithfulness score.

        Measures how much of the answer is supported by the context.

        Args:
            answer: Generated answer
            documents: Source documents

        Returns:
            Faithfulness score between 0 and 1
        """
        if not answer or not documents:
            return 0.0

        # Combine all document content
        context = " ".join([doc.page_content for doc in documents])
        context_lower = context.lower()

        # Split answer into sentences
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        # Check how many sentences have support in context
        supported = 0
        for sentence in sentences:
            # Simple check: are key terms from sentence in context?
            sentence_terms = set(sentence.lower().split())
            # Remove stop words (simplified)
            sentence_terms = {t for t in sentence_terms
                            if len(t) > 3 and t not in ['this', 'that', 'with', 'from']}

            if not sentence_terms:
                continue

            # Check if at least 50% of terms appear in context
            terms_in_context = sum(1 for term in sentence_terms if term in context_lower)
            if terms_in_context / len(sentence_terms) >= 0.5:
                supported += 1

        return supported / len(sentences)

    @staticmethod
    def context_recall(ground_truth: str, documents: List[Document]) -> float:
        """Calculate context recall.

        Measures if all relevant information from ground truth is in retrieved docs.

        Args:
            ground_truth: Expected information
            documents: Retrieved documents

        Returns:
            Recall score between 0 and 1
        """
        if not ground_truth or not documents:
            return 0.0

        truth_terms = set(ground_truth.lower().split())
        context = " ".join([doc.page_content for doc in documents]).lower()

        recalled_terms = sum(1 for term in truth_terms if term in context)
        return recalled_terms / len(truth_terms) if truth_terms else 0.0

    @staticmethod
    def context_precision(query: str, documents: List[Document],
                         relevant_indices: List[int] = None) -> float:
        """Calculate context precision.

        Measures the proportion of relevant documents in retrieved set.

        Args:
            query: User query
            documents: Retrieved documents
            relevant_indices: Indices of relevant documents (if known)

        Returns:
            Precision score between 0 and 1
        """
        if not documents:
            return 0.0

        if relevant_indices is None:
            # Estimate based on retrieval scores
            relevant_count = sum(
                1 for doc in documents
                if doc.metadata.get('retrieval_score', 0) > 0.5
            )
        else:
            relevant_count = len(relevant_indices)

        return relevant_count / len(documents)

    @staticmethod
    def answer_similarity(generated_answer: str, ground_truth: str) -> float:
        """Calculate similarity between generated answer and ground truth.

        Args:
            generated_answer: Generated answer
            ground_truth: Expected answer

        Returns:
            Similarity score between 0 and 1
        """
        if not generated_answer or not ground_truth:
            return 0.0

        gen_terms = set(generated_answer.lower().split())
        truth_terms = set(ground_truth.lower().split())

        intersection = len(gen_terms.intersection(truth_terms))
        union = len(gen_terms.union(truth_terms))

        return intersection / union if union > 0 else 0.0

    @staticmethod
    def compute_all_metrics(query: str, answer: str,
                           documents: List[Document],
                           ground_truth: str = None) -> Dict[str, float]:
        """Compute all available metrics.

        Args:
            query: User query
            answer: Generated answer
            documents: Retrieved documents
            ground_truth: Expected answer (optional)

        Returns:
            Dictionary of all metrics
        """
        metrics = {
            "context_relevancy": RAGMetrics.context_relevancy(query, documents),
            "answer_relevancy": RAGMetrics.answer_relevancy(query, answer),
            "faithfulness": RAGMetrics.faithfulness(answer, documents),
            "context_precision": RAGMetrics.context_precision(query, documents),
        }

        if ground_truth:
            metrics["context_recall"] = RAGMetrics.context_recall(ground_truth, documents)
            metrics["answer_similarity"] = RAGMetrics.answer_similarity(answer, ground_truth)

        # Compute average score
        metrics["average_score"] = sum(metrics.values()) / len(metrics)

        return metrics

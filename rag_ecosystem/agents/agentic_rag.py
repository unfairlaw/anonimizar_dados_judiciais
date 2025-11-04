"""Self-correcting Agentic RAG implementation."""

from typing import Dict, List, Optional, Any
from langchain_core.documents import Document
from langchain_core.language_models import BaseLLM
from rag_ecosystem.config.settings import get_settings
from rag_ecosystem.components.query_transformation import QueryTransformer
from rag_ecosystem.components.routing import QueryRouter
from rag_ecosystem.components.retrieval import DocumentRetriever
from rag_ecosystem.components.reranking import DocumentReranker
from rag_ecosystem.components.generation import ResponseGenerator
from rag_ecosystem.agents.document_grader import DocumentGrader
from rag_ecosystem.agents.response_evaluator import ResponseEvaluator


class AgenticRAG:
    """Self-correcting Agentic RAG system with multi-step reasoning."""

    def __init__(self, llm: Optional[BaseLLM] = None):
        """Initialize the Agentic RAG system.

        Args:
            llm: Language model to use (shared across components)
        """
        self.settings = get_settings()

        # Initialize all components
        self.query_transformer = QueryTransformer(llm)
        self.router = QueryRouter(llm)
        self.retriever = DocumentRetriever()
        self.reranker = DocumentReranker()
        self.generator = ResponseGenerator(llm)
        self.grader = DocumentGrader(llm)
        self.evaluator = ResponseEvaluator(llm)

        # Tracking
        self.history: List[Dict[str, Any]] = []

    def _log_step(self, step: str, data: Dict[str, Any]) -> None:
        """Log a step in the RAG process.

        Args:
            step: Step name
            data: Step data
        """
        self.history.append({
            "step": step,
            "data": data
        })

    def query(self, query: str, enable_self_correction: bool = None) -> Dict[str, Any]:
        """Execute a RAG query with self-correction.

        Args:
            query: User query
            enable_self_correction: Override settings for self-correction

        Returns:
            Dictionary with answer and metadata
        """
        if enable_self_correction is None:
            enable_self_correction = self.settings.self_correction_enabled

        self.history = []  # Reset history
        self._log_step("original_query", {"query": query})

        # Step 1: Check ambiguity
        ambiguity_check = self.query_transformer.check_ambiguity(query)
        self._log_step("ambiguity_check", ambiguity_check)

        if ambiguity_check["ambiguous"]:
            return {
                "status": "clarification_needed",
                "query": query,
                "ambiguity": ambiguity_check,
                "history": self.history
            }

        # Step 2: Route query
        route = self.router.route_query(query)
        self._log_step("routing", {"route": route})

        # If direct LLM, skip retrieval
        if route == "direct_llm":
            answer = self.generator.generate(query, [])
            return {
                "status": "success",
                "query": query,
                "answer": answer,
                "route": route,
                "documents": [],
                "history": self.history
            }

        # Step 3: Query transformation
        transformed_query = self.query_transformer.transform_query(query)
        self._log_step("query_transformation", {
            "original": query,
            "transformed": transformed_query
        })

        # Attempt retrieval with self-correction
        max_attempts = self.settings.max_correction_iterations if enable_self_correction else 1

        for attempt in range(max_attempts):
            self._log_step(f"attempt_{attempt + 1}", {"query": transformed_query})

            # Step 4: Retrieve documents
            documents = self.retriever.retrieve(
                transformed_query,
                method=self.settings.retrieval_method
            )
            self._log_step(f"retrieval_{attempt + 1}", {
                "num_documents": len(documents),
                "method": self.settings.retrieval_method
            })

            if not documents:
                if attempt < max_attempts - 1:
                    # Rewrite query and retry
                    transformed_query = self.query_transformer.rewrite_query(transformed_query)
                    continue
                else:
                    return {
                        "status": "no_documents_found",
                        "query": query,
                        "answer": "I couldn't find relevant information to answer your question.",
                        "history": self.history
                    }

            # Step 5: Grade documents
            relevant_documents = self.grader.filter_relevant(
                query,
                documents,
                threshold=self.settings.relevance_threshold * 10
            )
            self._log_step(f"grading_{attempt + 1}", {
                "original_count": len(documents),
                "relevant_count": len(relevant_documents)
            })

            # If no relevant documents, retry with rewritten query
            if not relevant_documents and attempt < max_attempts - 1:
                transformed_query = self.query_transformer.rewrite_query(transformed_query)
                continue

            # Use original documents if grading filters out everything
            documents_for_reranking = relevant_documents if relevant_documents else documents

            # Step 6: Rerank documents
            if self.settings.reranking_enabled:
                reranked_documents = self.reranker.rerank(
                    query,
                    documents_for_reranking
                )
                self._log_step(f"reranking_{attempt + 1}", {
                    "count": len(reranked_documents)
                })
            else:
                reranked_documents = documents_for_reranking[:self.settings.reranking_top_k]

            # Step 7: Generate answer
            answer = self.generator.generate(query, reranked_documents)
            self._log_step(f"generation_{attempt + 1}", {
                "answer_length": len(answer)
            })

            # Step 8: Evaluate answer
            if enable_self_correction:
                evaluation = self.evaluator.comprehensive_evaluation(
                    query,
                    answer,
                    reranked_documents
                )
                self._log_step(f"evaluation_{attempt + 1}", evaluation)

                # If answer is good, return it
                if evaluation["overall_verdict"]:
                    return {
                        "status": "success",
                        "query": query,
                        "answer": answer,
                        "documents": reranked_documents,
                        "evaluation": evaluation,
                        "attempts": attempt + 1,
                        "history": self.history
                    }

                # Otherwise, retry with query rewrite
                if attempt < max_attempts - 1:
                    transformed_query = self.query_transformer.rewrite_query(transformed_query)
                    continue
            else:
                # No evaluation, return answer
                return {
                    "status": "success",
                    "query": query,
                    "answer": answer,
                    "documents": reranked_documents,
                    "attempts": attempt + 1,
                    "history": self.history
                }

        # Max attempts reached, return best effort
        return {
            "status": "max_attempts_reached",
            "query": query,
            "answer": answer,
            "documents": reranked_documents,
            "attempts": max_attempts,
            "history": self.history
        }

    def multi_hop_query(self, query: str) -> Dict[str, Any]:
        """Execute a multi-hop query by decomposing into sub-queries.

        Args:
            query: Complex query requiring multiple retrieval steps

        Returns:
            Dictionary with answer and metadata
        """
        # Decompose query
        sub_queries = self.query_transformer.decompose_query(query)
        self._log_step("query_decomposition", {
            "original": query,
            "sub_queries": sub_queries
        })

        # Execute each sub-query
        sub_results = []
        all_documents = []

        for i, sub_query in enumerate(sub_queries):
            result = self.query(sub_query, enable_self_correction=False)
            sub_results.append({
                "sub_query": sub_query,
                "answer": result.get("answer", ""),
                "documents": result.get("documents", [])
            })
            all_documents.extend(result.get("documents", []))

        # Combine results
        combined_context = f"Based on the following information:\n\n"
        for i, result in enumerate(sub_results, 1):
            combined_context += f"{i}. {result['sub_query']}\n"
            combined_context += f"   Answer: {result['answer']}\n\n"

        # Generate final answer
        final_answer = self.generator.generate(query, all_documents)

        return {
            "status": "success",
            "query": query,
            "answer": final_answer,
            "sub_queries": sub_results,
            "total_documents": len(all_documents),
            "history": self.history
        }

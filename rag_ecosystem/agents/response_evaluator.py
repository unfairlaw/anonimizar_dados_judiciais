"""Response evaluation and hallucination detection module."""

from typing import Dict, List, Optional
from langchain_core.documents import Document
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from rag_ecosystem.config.settings import get_settings
from rag_ecosystem.config.prompts import SystemPrompts


class ResponseEvaluator:
    """Evaluates generated responses for quality and hallucinations."""

    def __init__(self, llm: Optional[BaseLLM] = None):
        """Initialize the response evaluator.

        Args:
            llm: Language model to use for evaluation
        """
        self.settings = get_settings()
        self.llm = llm or self._initialize_llm()
        self.prompts = SystemPrompts()

    def _initialize_llm(self) -> BaseLLM:
        """Initialize the language model based on settings."""
        if self.settings.llm_provider == "openai":
            return ChatOpenAI(
                model=self.settings.llm_model,
                temperature=0.0,
                api_key=self.settings.openai_api_key,
            )
        else:
            raise NotImplementedError(
                f"LLM provider {self.settings.llm_provider} not implemented"
            )

    def evaluate_answer(self, query: str, answer: str,
                       context: List[Document]) -> Dict:
        """Evaluate the quality of a generated answer.

        Args:
            query: Original user query
            answer: Generated answer
            context: Retrieved documents used for generation

        Returns:
            Evaluation results with scores and feedback
        """
        context_text = "\n\n".join([doc.page_content for doc in context])

        prompt = PromptTemplate.from_template(self.prompts.ANSWER_EVALUATOR)
        chain = prompt | self.llm

        response = chain.invoke({
            "question": query,
            "context": context_text,
            "answer": answer
        })

        content = response.content.strip()

        # Parse the response
        scores = {
            "relevance": 0,
            "faithfulness": 0,
            "completeness": 0,
            "overall": 0
        }

        explanation = ""

        for line in content.split('\n'):
            line_lower = line.lower()
            if "relevance:" in line_lower:
                scores["relevance"] = self._extract_score(line)
            elif "faithfulness:" in line_lower:
                scores["faithfulness"] = self._extract_score(line)
            elif "completeness:" in line_lower:
                scores["completeness"] = self._extract_score(line)
            elif "overall:" in line_lower:
                scores["overall"] = self._extract_score(line)
            elif "explanation:" in line_lower:
                explanation = line.split(":", 1)[1].strip()

        # Calculate overall if not provided
        if scores["overall"] == 0 and any(scores.values()):
            scores["overall"] = sum([
                scores["relevance"],
                scores["faithfulness"],
                scores["completeness"]
            ]) / 3

        return {
            "scores": scores,
            "explanation": explanation,
            "passes_quality_check": scores["overall"] >= 7.0,
            "needs_improvement": scores["overall"] < 7.0
        }

    def _extract_score(self, text: str) -> float:
        """Extract numeric score from text."""
        import re
        numbers = re.findall(r'\d+\.?\d*', text)
        if numbers:
            return float(numbers[0])
        return 0.0

    def check_hallucination(self, answer: str,
                           context: List[Document]) -> Dict:
        """Check if an answer contains hallucinations.

        Args:
            answer: Generated answer
            context: Retrieved documents

        Returns:
            Hallucination detection results
        """
        context_text = "\n\n".join([doc.page_content for doc in context])

        prompt = PromptTemplate.from_template(self.prompts.HALLUCINATION_CHECKER)
        chain = prompt | self.llm

        response = chain.invoke({
            "context": context_text,
            "answer": answer
        })

        content = response.content.strip()

        # Parse response
        hallucination_detected = "YES" in content.split('\n')[0].upper()

        explanation = ""
        problematic_statements = []

        for line in content.split('\n'):
            if "Explanation:" in line:
                explanation = line.split(":", 1)[1].strip()
            elif "Problematic Statements:" in line:
                # Extract following lines as statements
                idx = content.index(line)
                remaining = content[idx:].split('\n')[1:]
                problematic_statements = [
                    line.strip().lstrip('-*•1234567890.) ')
                    for line in remaining
                    if line.strip()
                ]

        return {
            "hallucination_detected": hallucination_detected,
            "explanation": explanation,
            "problematic_statements": problematic_statements,
            "is_trustworthy": not hallucination_detected
        }

    def comprehensive_evaluation(self, query: str, answer: str,
                                context: List[Document]) -> Dict:
        """Perform comprehensive evaluation including quality and hallucinations.

        Args:
            query: User query
            answer: Generated answer
            context: Retrieved documents

        Returns:
            Complete evaluation results
        """
        quality_eval = self.evaluate_answer(query, answer, context)
        hallucination_check = self.check_hallucination(answer, context)

        return {
            "query": query,
            "answer": answer,
            "quality": quality_eval,
            "hallucination": hallucination_check,
            "overall_verdict": (
                quality_eval["passes_quality_check"] and
                hallucination_check["is_trustworthy"]
            ),
            "should_regenerate": (
                not quality_eval["passes_quality_check"] or
                hallucination_check["hallucination_detected"]
            )
        }

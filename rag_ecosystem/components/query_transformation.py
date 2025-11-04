"""Query transformation and rewriting module."""

from typing import List, Optional
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from rag_ecosystem.config.settings import get_settings
from rag_ecosystem.config.prompts import SystemPrompts


class QueryTransformer:
    """Handles query transformation including rewriting and decomposition."""

    def __init__(self, llm: Optional[BaseLLM] = None):
        """Initialize the query transformer.

        Args:
            llm: Language model to use for query transformation
        """
        self.settings = get_settings()
        self.llm = llm or self._initialize_llm()
        self.prompts = SystemPrompts()

    def _initialize_llm(self) -> BaseLLM:
        """Initialize the language model based on settings."""
        if self.settings.llm_provider == "openai":
            return ChatOpenAI(
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
                api_key=self.settings.openai_api_key,
            )
        else:
            raise NotImplementedError(
                f"LLM provider {self.settings.llm_provider} not implemented"
            )

    def rewrite_query(self, query: str) -> str:
        """Rewrite a query to improve retrieval performance.

        Args:
            query: Original user query

        Returns:
            Rewritten query optimized for semantic search
        """
        prompt = PromptTemplate.from_template(self.prompts.QUERY_REWRITER)
        chain = prompt | self.llm

        response = chain.invoke({"query": query})
        rewritten_query = response.content.strip()

        return rewritten_query

    def decompose_query(self, query: str) -> List[str]:
        """Decompose a complex query into simpler sub-queries.

        Args:
            query: Complex user query

        Returns:
            List of simpler sub-queries
        """
        prompt = PromptTemplate.from_template(self.prompts.QUERY_DECOMPOSITION)
        chain = prompt | self.llm

        response = chain.invoke({"query": query})

        # Parse the numbered list
        sub_queries = []
        for line in response.content.strip().split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                # Remove numbering and clean up
                cleaned = line.lstrip('0123456789.-*) ').strip()
                if cleaned:
                    sub_queries.append(cleaned)

        return sub_queries or [query]  # Return original if parsing fails

    def check_ambiguity(self, query: str) -> dict:
        """Check if a query is ambiguous and needs clarification.

        Args:
            query: User query to check

        Returns:
            Dictionary with ambiguity status and clarifying questions
        """
        prompt = PromptTemplate.from_template(self.prompts.QUERY_AMBIGUITY_CHECKER)
        chain = prompt | self.llm

        response = chain.invoke({"query": query})
        content = response.content.strip()

        # Parse the response
        result = {
            "ambiguous": "YES" in content.split('\n')[0].upper(),
            "reason": "",
            "clarifying_questions": []
        }

        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "Reason:" in line:
                result["reason"] = line.split("Reason:", 1)[1].strip()
            elif "Clarifying Questions:" in line and i + 1 < len(lines):
                # Get questions from following lines
                for q_line in lines[i+1:]:
                    if q_line.strip() and (q_line[0].isdigit() or q_line.startswith('-')):
                        question = q_line.lstrip('0123456789.-*) ').strip()
                        if question:
                            result["clarifying_questions"].append(question)

        return result

    def transform_query(self, query: str, enable_rewrite: bool = None) -> str:
        """Main method to transform a query with all enabled transformations.

        Args:
            query: Original user query
            enable_rewrite: Override settings for query rewriting

        Returns:
            Transformed query
        """
        if enable_rewrite is None:
            enable_rewrite = self.settings.query_rewriting_enabled

        if enable_rewrite:
            return self.rewrite_query(query)

        return query

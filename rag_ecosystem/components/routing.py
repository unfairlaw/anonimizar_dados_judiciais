"""Intelligent query routing module."""

from typing import Literal, Optional
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate
from rag_ecosystem.config.settings import get_settings
from rag_ecosystem.config.prompts import SystemPrompts
from rag_ecosystem.utils.llm_factory import create_llm


DataSource = Literal["vector_store", "web_search", "direct_llm"]


class QueryRouter:
    """Routes queries to the most appropriate data source."""

    def __init__(self, llm: Optional[BaseLLM] = None):
        """Initialize the query router.

        Args:
            llm: Language model to use for routing decisions
        """
        self.settings = get_settings()
        self.llm = llm or self._initialize_llm()
        self.prompts = SystemPrompts()

    def _initialize_llm(self) -> BaseLLM:
        """Initialize the language model based on settings."""
        return create_llm(temperature=0.0)
    def route_query(self, query: str) -> DataSource:
        """Determine the best data source for a given query.

        Args:
            query: User query to route

        Returns:
            Data source identifier (vector_store, web_search, or direct_llm)
        """
        if not self.settings.routing_enabled:
            return "vector_store"  # Default to vector store if routing disabled

        prompt = PromptTemplate.from_template(self.prompts.ROUTING_DECISION)
        chain = prompt | self.llm

        response = chain.invoke({"query": query})
        decision = response.content.strip().lower()

        # Parse the decision
        if "web_search" in decision:
            if not self.settings.enable_web_search:
                return "vector_store"  # Fall back if web search disabled
            return "web_search"
        elif "direct_llm" in decision:
            return "direct_llm"
        else:
            return "vector_store"

    def route_with_explanation(self, query: str) -> dict:
        """Route query and provide explanation for the decision.

        Args:
            query: User query to route

        Returns:
            Dictionary with route and explanation
        """
        route = self.route_query(query)

        explanations = {
            "vector_store": "Query requires information from the knowledge base",
            "web_search": "Query needs up-to-date information from the web",
            "direct_llm": "Query can be answered with general knowledge"
        }

        return {
            "route": route,
            "explanation": explanations[route]
        }

    def is_time_sensitive(self, query: str) -> bool:
        """Check if a query requires time-sensitive information.

        Args:
            query: User query to analyze

        Returns:
            True if query is time-sensitive
        """
        time_keywords = [
            "current", "latest", "recent", "today", "now",
            "2024", "2025", "this year", "this month",
            "breaking", "news", "updated"
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in time_keywords)

    def requires_external_knowledge(self, query: str) -> bool:
        """Check if query likely requires external/web knowledge.

        Args:
            query: User query to analyze

        Returns:
            True if external knowledge is likely needed
        """
        external_indicators = [
            "what is", "who is", "when did", "how to",
            "define", "explain", "weather", "stock price"
        ]

        query_lower = query.lower()
        return any(indicator in query_lower for indicator in external_indicators)

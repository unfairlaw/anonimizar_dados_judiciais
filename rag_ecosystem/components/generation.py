"""Response generation module."""

from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from rag_ecosystem.config.settings import get_settings
from rag_ecosystem.config.prompts import SystemPrompts


class ResponseGenerator:
    """Generates responses using retrieved context and LLM."""

    def __init__(self, llm: Optional[BaseLLM] = None):
        """Initialize the response generator.

        Args:
            llm: Language model to use for generation
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
                max_tokens=self.settings.llm_max_tokens,
                api_key=self.settings.openai_api_key,
            )
        else:
            raise NotImplementedError(
                f"LLM provider {self.settings.llm_provider} not implemented"
            )

    def _format_context(self, documents: List[Document]) -> str:
        """Format retrieved documents into context string.

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant context found."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source', 'Unknown')
            score = doc.metadata.get('reranking_score') or doc.metadata.get('retrieval_score', 0)

            context_parts.append(
                f"[Document {i}] (Source: {source}, Relevance: {score:.3f})\n"
                f"{doc.page_content}\n"
            )

        return "\n".join(context_parts)

    def generate(self, query: str, documents: List[Document]) -> str:
        """Generate a response to the query using retrieved documents.

        Args:
            query: User query
            documents: Retrieved and reranked documents

        Returns:
            Generated response
        """
        context = self._format_context(documents)

        prompt = PromptTemplate.from_template(self.prompts.ANSWER_GENERATOR)
        chain = prompt | self.llm

        response = chain.invoke({
            "context": context,
            "question": query
        })

        return response.content.strip()

    def generate_with_metadata(self, query: str,
                              documents: List[Document]) -> Dict[str, Any]:
        """Generate response with additional metadata.

        Args:
            query: User query
            documents: Retrieved documents

        Returns:
            Dictionary with response and metadata
        """
        answer = self.generate(query, documents)

        # Extract sources
        sources = list(set(
            doc.metadata.get('source', 'Unknown')
            for doc in documents
        ))

        # Calculate average relevance
        avg_relevance = sum(
            doc.metadata.get('reranking_score',
                           doc.metadata.get('retrieval_score', 0))
            for doc in documents
        ) / len(documents) if documents else 0

        return {
            "answer": answer,
            "sources": sources,
            "num_documents_used": len(documents),
            "average_relevance": avg_relevance,
            "query": query
        }

    def summarize_context(self, documents: List[Document]) -> str:
        """Summarize the retrieved context.

        Args:
            documents: Documents to summarize

        Returns:
            Summary of the context
        """
        if not documents:
            return "No context available."

        context = self._format_context(documents)

        prompt = PromptTemplate.from_template(self.prompts.CONTEXT_SUMMARIZER)
        chain = prompt | self.llm

        response = chain.invoke({"documents": context})

        return response.content.strip()

    def generate_streaming(self, query: str, documents: List[Document]):
        """Generate response with streaming output.

        Args:
            query: User query
            documents: Retrieved documents

        Yields:
            Chunks of generated text
        """
        context = self._format_context(documents)

        prompt = PromptTemplate.from_template(self.prompts.ANSWER_GENERATOR)
        chain = prompt | self.llm

        for chunk in chain.stream({
            "context": context,
            "question": query
        }):
            if hasattr(chunk, 'content'):
                yield chunk.content
            else:
                yield str(chunk)

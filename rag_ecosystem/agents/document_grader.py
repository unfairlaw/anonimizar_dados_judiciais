"""Document grading module for assessing relevance."""

from typing import List, Dict, Optional
from langchain_core.documents import Document
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from rag_ecosystem.config.settings import get_settings
from rag_ecosystem.config.prompts import SystemPrompts


class DocumentGrader:
    """Grades the relevance of retrieved documents to a query."""

    def __init__(self, llm: Optional[BaseLLM] = None):
        """Initialize the document grader.

        Args:
            llm: Language model to use for grading
        """
        self.settings = get_settings()
        self.llm = llm or self._initialize_llm()
        self.prompts = SystemPrompts()

    def _initialize_llm(self) -> BaseLLM:
        """Initialize the language model based on settings."""
        if self.settings.llm_provider == "openai":
            return ChatOpenAI(
                model=self.settings.llm_model,
                temperature=0.0,  # Use zero temperature for consistent grading
                api_key=self.settings.openai_api_key,
            )
        else:
            raise NotImplementedError(
                f"LLM provider {self.settings.llm_provider} not implemented"
            )

    def grade_document(self, query: str, document: Document) -> Dict:
        """Grade a single document's relevance to the query.

        Args:
            query: User query
            document: Document to grade

        Returns:
            Dictionary with score and explanation
        """
        prompt = PromptTemplate.from_template(self.prompts.DOCUMENT_GRADER)
        chain = prompt | self.llm

        response = chain.invoke({
            "question": query,
            "document": document.page_content
        })

        content = response.content.strip()

        # Parse the response
        score = 0
        explanation = content

        # Try to extract numeric score
        for line in content.split('\n'):
            if any(char.isdigit() for char in line):
                # Extract first number found
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    score = int(numbers[0])
                    break

        return {
            "score": score,
            "explanation": explanation,
            "is_relevant": score >= self.settings.relevance_threshold * 10,
            "document": document
        }

    def grade_documents(self, query: str,
                       documents: List[Document]) -> List[Dict]:
        """Grade multiple documents.

        Args:
            query: User query
            documents: List of documents to grade

        Returns:
            List of grading results
        """
        results = []
        for doc in documents:
            result = self.grade_document(query, doc)
            results.append(result)

        return results

    def filter_relevant(self, query: str,
                       documents: List[Document],
                       threshold: Optional[float] = None) -> List[Document]:
        """Filter documents to keep only relevant ones.

        Args:
            query: User query
            documents: List of documents to filter
            threshold: Minimum relevance score (0-10 scale)

        Returns:
            List of relevant documents
        """
        if threshold is None:
            threshold = self.settings.relevance_threshold * 10

        graded = self.grade_documents(query, documents)

        relevant_docs = [
            result['document']
            for result in graded
            if result['score'] >= threshold
        ]

        # Update metadata with grading scores
        for doc, result in zip(relevant_docs, graded):
            doc.metadata['grade_score'] = result['score']
            doc.metadata['grade_explanation'] = result['explanation']

        return relevant_docs

    def get_best_documents(self, query: str,
                          documents: List[Document],
                          top_k: int = 3) -> List[Document]:
        """Get the top-k most relevant documents.

        Args:
            query: User query
            documents: List of documents
            top_k: Number of top documents to return

        Returns:
            Top-k relevant documents
        """
        graded = self.grade_documents(query, documents)

        # Sort by score
        sorted_results = sorted(graded,
                              key=lambda x: x['score'],
                              reverse=True)

        # Get top-k and update metadata
        top_docs = []
        for result in sorted_results[:top_k]:
            doc = result['document']
            doc.metadata['grade_score'] = result['score']
            doc.metadata['grade_explanation'] = result['explanation']
            top_docs.append(doc)

        return top_docs

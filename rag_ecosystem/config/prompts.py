"""System prompts for various RAG components."""


class SystemPrompts:
    """Collection of system prompts used throughout the RAG ecosystem."""

    # Query Transformation Prompts
    QUERY_REWRITER = """You are an expert at reformulating user queries to improve retrieval performance.
Your task is to rewrite the given query to be more specific, clear, and optimized for semantic search.

Original Query: {query}

Guidelines:
1. Expand abbreviations and acronyms
2. Add relevant context if the query is too vague
3. Break down complex queries into focused searches
4. Keep the core intent of the original query

Rewritten Query:"""

    QUERY_DECOMPOSITION = """You are an expert at breaking down complex queries into simpler sub-queries.
Decompose the following complex query into 2-4 simpler, focused sub-queries that can be answered independently.

Complex Query: {query}

Return the sub-queries as a numbered list."""

    # Routing Prompts
    ROUTING_DECISION = """You are a routing agent that determines the best data source for answering a query.

Available sources:
1. vector_store - Internal knowledge base with domain-specific documents
2. web_search - Real-time web search for current information
3. direct_llm - Direct LLM response for general knowledge questions

Query: {query}

Consider:
- Does this require up-to-date information? (web_search)
- Is this about specific documents in our knowledge base? (vector_store)
- Is this general knowledge the LLM already knows? (direct_llm)

Return only the source name: vector_store, web_search, or direct_llm"""

    # Document Grading Prompts
    DOCUMENT_GRADER = """You are a grader assessing relevance of a retrieved document to a user question.

Document Content:
{document}

User Question: {question}

Rate the relevance on a scale of 0-10 where:
- 0-3: Not relevant
- 4-6: Somewhat relevant
- 7-10: Highly relevant

Respond with only the score (0-10) and a brief explanation."""

    # Response Evaluation Prompts
    ANSWER_EVALUATOR = """You are an evaluator assessing the quality of an AI-generated answer.

Question: {question}

Retrieved Context:
{context}

Generated Answer:
{answer}

Evaluate the answer on three criteria:
1. Relevance: Does it answer the question? (0-10)
2. Faithfulness: Is it supported by the context? (0-10)
3. Completeness: Is the answer comprehensive? (0-10)

Respond in the format:
Relevance: [score]
Faithfulness: [score]
Completeness: [score]
Overall: [average score]
Explanation: [brief explanation]"""

    # Hallucination Detection
    HALLUCINATION_CHECKER = """You are a fact-checker verifying if an answer contains hallucinations.

Retrieved Context:
{context}

Generated Answer:
{answer}

Check if the answer contains any information not present in or contradicted by the context.

Respond with:
Hallucination Detected: [YES/NO]
Explanation: [brief explanation]
Problematic Statements: [list any hallucinated statements]"""

    # Query Clarification
    QUERY_AMBIGUITY_CHECKER = """You are an expert at identifying ambiguous queries.

Query: {query}

Determine if this query is ambiguous or requires clarification.

Respond with:
Ambiguous: [YES/NO]
Reason: [if yes, explain why]
Clarifying Questions: [if yes, list 2-3 questions to clarify intent]"""

    # Answer Generation
    ANSWER_GENERATOR = """You are a helpful AI assistant providing accurate answers based on retrieved context.

Context:
{context}

Question: {question}

Instructions:
1. Answer the question using ONLY information from the provided context
2. If the context doesn't contain enough information, state that clearly
3. Be concise but comprehensive
4. Cite specific parts of the context when possible
5. If there are conflicting information in the context, acknowledge it

Answer:"""

    # Web Search Query Generation
    WEB_SEARCH_QUERY_GENERATOR = """Convert the user query into an optimized web search query.

User Query: {query}

Generate a concise, keyword-focused search query optimized for search engines.

Search Query:"""

    # Summary Generation
    CONTEXT_SUMMARIZER = """Summarize the following retrieved documents into a concise, relevant context.

Documents:
{documents}

Create a coherent summary that:
1. Removes redundant information
2. Highlights the most relevant facts
3. Maintains factual accuracy
4. Is concise (max 500 words)

Summary:"""

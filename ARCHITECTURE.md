# RAG Ecosystem Architecture

## Overview

This document describes the architecture of the RAG Ecosystem, a production-ready Retrieval-Augmented Generation system with self-correction capabilities.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       User Query                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Query Transformation Layer                      │
│  • Query Rewriting                                          │
│  • Query Decomposition                                      │
│  • Ambiguity Detection                                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Routing Layer                               │
│  Decision: Vector Store | Web Search | Direct LLM          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Retrieval Layer                             │
│  • Vector Search (Semantic)                                 │
│  • Keyword Search (BM25)                                    │
│  • Hybrid Search (Combined)                                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Document Grading Layer                         │
│  • LLM-based Relevance Scoring                             │
│  • Threshold-based Filtering                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                Reranking Layer                              │
│  • Cross-encoder Scoring                                    │
│  • Top-K Selection                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│               Generation Layer                              │
│  • Context-aware Generation                                 │
│  • Source Citation                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Evaluation Layer                               │
│  • Quality Assessment                                       │
│  • Hallucination Detection                                  │
│  • Decision: Accept or Retry                                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
                   [Response]
```

## Component Details

### 1. Query Transformation Layer

**Purpose**: Optimize user queries for better retrieval performance.

**Components**:
- `QueryTransformer`: Main transformation class

**Operations**:
- **Query Rewriting**: Reformulates vague or poorly-structured queries
- **Query Decomposition**: Breaks complex queries into simpler sub-queries
- **Ambiguity Detection**: Identifies queries that need clarification

**Example Flow**:
```
User: "Tell me about ML"
↓ Query Rewriting
System: "Explain machine learning concepts and applications"
```

### 2. Routing Layer

**Purpose**: Direct queries to the most appropriate data source.

**Components**:
- `QueryRouter`: Intelligent routing decision maker

**Routing Options**:
1. **Vector Store**: Internal knowledge base queries
2. **Web Search**: Time-sensitive or current event queries
3. **Direct LLM**: General knowledge questions

**Decision Factors**:
- Time sensitivity
- Query type
- Knowledge domain

### 3. Indexing Layer

**Purpose**: Convert documents into searchable embeddings.

**Components**:
- `DocumentIndexer`: Handles document processing and indexing

**Process**:
1. **Document Loading**: Read from various sources
2. **Chunking**: Split documents into optimal chunks
   - Chunk size: 1000 tokens
   - Overlap: 200 tokens
3. **Embedding**: Convert text to vector representations
4. **Storage**: Store in vector database (ChromaDB/FAISS)

**Metadata Tracking**:
```python
{
    "source": "document.pdf",
    "chunk_id": 0,
    "total_chunks": 10,
    "doc_id": "unique_id"
}
```

### 4. Retrieval Layer

**Purpose**: Find the most relevant documents for a query.

**Components**:
- `DocumentRetriever`: Multi-strategy retrieval system

**Retrieval Strategies**:

#### Vector Search
- Uses cosine similarity
- Semantic understanding
- Fast approximate nearest neighbor search

#### Keyword Search (BM25)
- Term frequency-based
- Good for exact matches
- Keyword-focused queries

#### Hybrid Search
- Combines vector and keyword
- Configurable weight (alpha)
- Best of both worlds

**Formula**:
```
hybrid_score = α × vector_score + (1 - α) × keyword_score
```

### 5. Document Grading Layer

**Purpose**: Filter out irrelevant documents before generation.

**Components**:
- `DocumentGrader`: LLM-based relevance assessment

**Process**:
1. LLM evaluates each document's relevance (0-10 scale)
2. Filter documents below threshold
3. Update metadata with grades

**Benefits**:
- Reduces noise in generation
- Improves answer quality
- Enables retry logic

### 6. Reranking Layer

**Purpose**: Precisely reorder documents using computationally expensive models.

**Components**:
- `DocumentReranker`: Cross-encoder based reranking

**Why Reranking?**
- Initial retrieval: Fast bi-encoders (efficiency)
- Reranking: Slow cross-encoders (accuracy)
- Best trade-off: Fast first pass, accurate second pass

**Models Used**:
- `cross-encoder/ms-marco-MiniLM-L-6-v2`

### 7. Generation Layer

**Purpose**: Generate responses based on retrieved context.

**Components**:
- `ResponseGenerator`: Context-aware answer generation

**Features**:
- Source citation
- Streaming support
- Context summarization
- Faithfulness to source material

**Prompt Structure**:
```
Context: [Retrieved Documents]
Question: [User Query]
Instructions: [Guidelines]
Answer:
```

### 8. Evaluation Layer

**Purpose**: Assess response quality and detect issues.

**Components**:
- `ResponseEvaluator`: Multi-metric evaluation
- `DocumentGrader`: Document-level assessment

**Metrics**:
1. **Relevance**: Does it answer the question?
2. **Faithfulness**: Is it supported by context?
3. **Completeness**: Is the answer comprehensive?

**Hallucination Detection**:
- Checks for unsupported claims
- Identifies contradictions
- Flags problematic statements

## Self-Correction Flow

The system implements a self-correcting loop:

```
┌─────────────┐
│   Query     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Retrieve   │
└──────┬──────┘
       │
       ▼
┌─────────────┐      Fail
│    Grade    ├────────────┐
└──────┬──────┘            │
       │ Pass              │
       ▼                   │
┌─────────────┐            │
│   Rerank    │            │
└──────┬──────┘            │
       │                   │
       ▼                   │
┌─────────────┐            │
│  Generate   │            │
└──────┬──────┘            │
       │                   │
       ▼                   │
┌─────────────┐      Fail  │
│  Evaluate   ├────────────┤
└──────┬──────┘            │
       │ Pass              │
       ▼                   ▼
   [Return]         [Rewrite Query]
                           │
                           └──────────┐
                                      │
                          Max Attempts? No
                                      │
                                     Yes
                                      ▼
                              [Return Best]
```

## Agentic RAG System

The `AgenticRAG` class orchestrates all components:

### Key Features:

1. **Stateful**: Tracks history of attempts
2. **Adaptive**: Adjusts strategy based on results
3. **Self-correcting**: Automatically retries with improvements
4. **Multi-hop**: Handles complex queries requiring multiple steps

### Retry Logic:

```python
for attempt in range(max_attempts):
    documents = retrieve(query)

    if not documents or low_quality(documents):
        query = rewrite(query)
        continue

    answer = generate(query, documents)

    if evaluate(answer) == "good":
        return answer

    query = rewrite(query)

return best_answer
```

## Data Flow Example

Let's trace a query through the system:

**User Query**: "What is machine learning?"

1. **Query Transformation**:
   - Rewritten: "Explain machine learning, its concepts, and applications"

2. **Routing**:
   - Decision: Vector Store (internal knowledge)

3. **Retrieval**:
   - Vector search: 5 documents
   - Keyword search: 5 documents
   - Hybrid merge: Top 5 combined

4. **Grading**:
   - Doc 1: 9/10 ✓
   - Doc 2: 8/10 ✓
   - Doc 3: 5/10 ✗
   - Doc 4: 9/10 ✓
   - Doc 5: 7/10 ✓
   - Filtered: 4 documents

5. **Reranking**:
   - Cross-encoder scores
   - Top 3 selected

6. **Generation**:
   - Answer generated from top 3 docs

7. **Evaluation**:
   - Relevance: 9/10
   - Faithfulness: 9/10
   - Completeness: 8/10
   - Overall: Pass ✓

8. **Return**: Answer with metadata

## Performance Considerations

### Latency Breakdown:

- Query transformation: ~100ms
- Routing decision: ~50ms
- Retrieval: ~200ms
- Document grading: ~500ms (parallel)
- Reranking: ~300ms
- Generation: ~1000ms
- Evaluation: ~500ms

**Total**: ~2.5s per query (with self-correction enabled)

### Optimization Strategies:

1. **Caching**: Cache embeddings and frequent queries
2. **Batching**: Process multiple documents in parallel
3. **Async**: Use async operations for I/O
4. **Model Selection**: Balance accuracy vs speed
5. **Selective Evaluation**: Skip for simple queries

## Scalability

### Horizontal Scaling:

- Vector store: Distributed ChromaDB/FAISS
- LLM: Load balancing across multiple instances
- Retrieval: Shard documents across multiple stores

### Vertical Scaling:

- GPU acceleration for embeddings
- Larger batch sizes
- More powerful models

## Security Considerations

1. **API Key Management**: Environment variables, secrets manager
2. **Input Validation**: Sanitize user queries
3. **Rate Limiting**: Prevent abuse
4. **Access Control**: Document-level permissions
5. **Audit Logging**: Track all queries and responses

## Future Enhancements

1. **Multi-modal RAG**: Support images, tables, charts
2. **Streaming Retrieval**: Progressive result loading
3. **Federated Search**: Multiple knowledge bases
4. **Active Learning**: Learn from user feedback
5. **Explainability**: Visualize decision process

## Conclusion

This architecture provides a robust, production-ready RAG system with:
- High accuracy through multi-stage retrieval and evaluation
- Reliability through self-correction
- Flexibility through modular design
- Observability through comprehensive metrics

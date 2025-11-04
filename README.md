# RAG Ecosystem - Production-Ready RAG System

A comprehensive, modular implementation of a Retrieval-Augmented Generation (RAG) system with self-correction capabilities, based on the latest research and best practices from 2025.

## 🌟 Features

### Core Components

1. **Query Transformations**
   - Query rewriting and optimization
   - Complex query decomposition
   - Ambiguity detection

2. **Intelligent Routing**
   - Dynamic query routing to appropriate data sources
   - Vector store, web search, or direct LLM routing
   - Context-aware decision making

3. **Advanced Indexing**
   - Multi-layered document chunking
   - Semantic embeddings with sentence-transformers
   - ChromaDB and FAISS support

4. **Hybrid Retrieval**
   - Vector similarity search
   - BM25 keyword search
   - Hybrid search combining both approaches

5. **Document Reranking**
   - Cross-encoder based reranking
   - Relevance-based filtering
   - Score threshold configuration

6. **Self-Correcting Agentic Flows**
   - Document relevance grading
   - Response quality evaluation
   - Hallucination detection
   - Automatic query retry with improvements

7. **End-to-End Evaluation**
   - Comprehensive metrics (relevancy, faithfulness, precision, recall)
   - Performance benchmarking
   - Detailed evaluation reports

## 📁 Project Structure

```
rag_ecosystem/
├── config/
│   ├── settings.py          # Configuration management
│   └── prompts.py           # System prompts
├── components/
│   ├── query_transformation.py
│   ├── routing.py
│   ├── indexing.py
│   ├── retrieval.py
│   ├── reranking.py
│   └── generation.py
├── agents/
│   ├── document_grader.py
│   ├── response_evaluator.py
│   └── agentic_rag.py       # Main agentic RAG system
├── evaluation/
│   ├── metrics.py
│   └── pipeline_evaluator.py
├── utils/
│   └── logger.py
└── examples/
    ├── basic_rag.py
    ├── agentic_rag_example.py
    └── evaluation_example.py
```

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd anonimizar_dados_judiciais
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

#### 1. Index Documents

```bash
# Index a single file
python main.py index /path/to/document.txt

# Index a directory
python main.py index /path/to/docs/ --pattern "*.txt"

# Clear and re-index
python main.py index /path/to/docs/ --clear
```

#### 2. Query the System

```bash
# Basic query
python main.py query "What is machine learning?"

# Show retrieved documents
python main.py query "What is RAG?" --show-docs

# Disable self-correction
python main.py query "Explain AI" --no-self-correct
```

#### 3. Interactive Mode

```bash
python main.py interactive
```

#### 4. View Statistics

```bash
python main.py stats
```

### Programmatic Usage

#### Basic RAG

```python
from rag_ecosystem.components.indexing import DocumentIndexer
from rag_ecosystem.components.retrieval import DocumentRetriever
from rag_ecosystem.components.generation import ResponseGenerator

# Index documents
indexer = DocumentIndexer()
indexer.index_from_text("Your document content here")

# Retrieve and generate
retriever = DocumentRetriever()
generator = ResponseGenerator()

docs = retriever.retrieve("Your query", method="hybrid")
answer = generator.generate("Your query", docs)
print(answer)
```

#### Agentic RAG with Self-Correction

```python
from rag_ecosystem.agents.agentic_rag import AgenticRAG
from rag_ecosystem.components.indexing import DocumentIndexer

# Index your documents
indexer = DocumentIndexer()
indexer.index_from_text("Your knowledge base content")

# Create agentic RAG system
rag = AgenticRAG()

# Query with self-correction
result = rag.query("Your question", enable_self_correction=True)

print(f"Answer: {result['answer']}")
print(f"Status: {result['status']}")
print(f"Attempts: {result['attempts']}")
print(f"Quality: {result.get('evaluation', {})}")
```

#### Multi-Hop Queries

```python
# For complex queries requiring multiple retrieval steps
result = rag.multi_hop_query(
    "Explain the components of RAG and how they work together"
)

print(f"Answer: {result['answer']}")
print(f"Sub-queries: {result['sub_queries']}")
```

## ⚙️ Configuration

Edit `rag_ecosystem/config/settings.py` or use environment variables:

```python
# LLM Configuration
llm_provider = "openai"  # openai, anthropic, ollama
llm_model = "gpt-4-turbo-preview"
llm_temperature = 0.0

# Retrieval Configuration
retrieval_method = "hybrid"  # vector, keyword, hybrid
retrieval_top_k = 5
hybrid_alpha = 0.5  # Balance between vector and keyword

# Reranking
reranking_enabled = True
reranking_top_k = 3

# Self-Correction
self_correction_enabled = True
max_correction_iterations = 3
relevance_threshold = 0.7
```

## 📊 Evaluation

Run comprehensive evaluations:

```python
from rag_ecosystem.evaluation.pipeline_evaluator import (
    PipelineEvaluator,
    EvaluationCase
)

# Define test cases
test_cases = [
    EvaluationCase(
        query="What is AI?",
        expected_answer="AI is artificial intelligence...",
    ),
    # Add more test cases
]

# Evaluate
evaluator = PipelineEvaluator(rag)
results = evaluator.evaluate_batch(test_cases)

# Generate report
print(evaluator.generate_report())

# Save results
evaluator.save_results("evaluation_results.json")
```

## 📈 Metrics

The system tracks the following metrics:

- **Context Relevancy**: How relevant retrieved documents are to the query
- **Answer Relevancy**: How well the answer addresses the query
- **Faithfulness**: Whether the answer is grounded in the retrieved context
- **Context Precision**: Proportion of relevant documents retrieved
- **Context Recall**: Coverage of relevant information
- **Answer Similarity**: Comparison with ground truth (if available)

## 🔧 Advanced Features

### Custom Components

You can replace any component with your own implementation:

```python
from langchain_openai import ChatOpenAI
from rag_ecosystem.agents.agentic_rag import AgenticRAG

# Use custom LLM
custom_llm = ChatOpenAI(model="gpt-4", temperature=0.5)
rag = AgenticRAG(llm=custom_llm)
```

### Web Search Integration

Enable web search for time-sensitive queries:

```python
from rag_ecosystem.config.settings import get_settings

settings = get_settings()
settings.enable_web_search = True
settings.routing_enabled = True
```

### Streaming Responses

```python
generator = ResponseGenerator()

for chunk in generator.generate_streaming(query, documents):
    print(chunk, end="", flush=True)
```

## 🧪 Examples

Run the provided examples:

```bash
# Basic RAG
python -m rag_ecosystem.examples.basic_rag

# Agentic RAG with self-correction
python -m rag_ecosystem.examples.agentic_rag_example

# Evaluation pipeline
python -m rag_ecosystem.examples.evaluation_example
```

## 🏗️ Architecture

The system implements a state-of-the-art RAG architecture:

```
Query → Query Transform → Route Decision
                              ↓
        [Vector Store | Web Search | Direct LLM]
                              ↓
                         Retrieve
                              ↓
                       Grade Documents
                              ↓
                          Rerank
                              ↓
                         Generate
                              ↓
                    Evaluate Response
                              ↓
              [Good] → Return   [Bad] → Retry
```

## 📚 References

This implementation is based on research and best practices from:

- "Building the Entire RAG Ecosystem and Optimizing Every Component" by Fareed Khan
- LangChain and LangGraph documentation
- Self-RAG and Corrective RAG papers
- Modern RAG architecture patterns (2025)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LangChain and LangGraph communities
- Sentence Transformers project
- ChromaDB team
- The RAG research community

## 📧 Contact

For questions or support, please open an issue on GitHub.

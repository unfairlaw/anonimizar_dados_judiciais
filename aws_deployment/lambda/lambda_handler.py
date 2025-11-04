"""AWS Lambda handler for RAG system."""

import json
import os
import sys
from typing import Dict, Any

# Add the package to Python path
sys.path.insert(0, "/opt/python")  # For Lambda layers
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_ecosystem.agents.agentic_rag import AgenticRAG
from rag_ecosystem.components.s3_loader import S3DocumentLoader
from rag_ecosystem.components.s3_vector_store import S3VectorStorePersistence
from rag_ecosystem.components.indexing import DocumentIndexer
from rag_ecosystem.config.settings import get_settings
from rag_ecosystem.utils.logger import setup_logger

logger = setup_logger("lambda_handler")

# Global variables for warm starts
_rag_system = None
_vector_store_synced = False


def initialize_rag_system() -> AgenticRAG:
    """Initialize RAG system with S3 vector store.

    Returns:
        Initialized AgenticRAG instance
    """
    global _rag_system, _vector_store_synced

    if _rag_system is not None and _vector_store_synced:
        logger.info("Using cached RAG system")
        return _rag_system

    logger.info("Initializing RAG system...")

    # Get S3 configuration
    bucket_name = os.environ.get("S3_BUCKET_NAME")
    vector_store_prefix = os.environ.get("S3_VECTOR_STORE_PREFIX", "vector_store")

    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable required")

    # Setup S3 vector store persistence
    s3_persistence = S3VectorStorePersistence(
        bucket_name=bucket_name,
        s3_prefix=vector_store_prefix,
        local_path="/tmp/vector_store",
    )

    # Download vector store from S3
    logger.info("Downloading vector store from S3...")
    _vector_store_synced = s3_persistence.sync_from_s3()

    if not _vector_store_synced:
        logger.warning("No vector store found in S3, starting with empty collection")

    # Update settings to use local path
    settings = get_settings()
    settings.vector_store_path = s3_persistence.get_local_path()

    # Initialize RAG system
    _rag_system = AgenticRAG()

    logger.info("RAG system initialized successfully")
    return _rag_system


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler function.

    Expected event structure:
    {
        "action": "query" | "index" | "stats",
        "query": "user question",  # for query action
        "s3_prefix": "docs/",      # for index action
        "file_pattern": ".txt"     # for index action
    }

    Args:
        event: Lambda event object
        context: Lambda context object

    Returns:
        Response dictionary
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Parse event
        action = event.get("action", "query")

        if action == "query":
            return handle_query(event)
        elif action == "index":
            return handle_index(event)
        elif action == "stats":
            return handle_stats()
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unknown action: {action}"})
            }

    except Exception as e:
        logger.exception("Error processing request")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "type": type(e).__name__
            })
        }


def handle_query(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle query action.

    Args:
        event: Lambda event

    Returns:
        Query response
    """
    query = event.get("query")
    if not query:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "query parameter required"})
        }

    enable_self_correction = event.get("enable_self_correction", True)

    # Initialize RAG system
    rag = initialize_rag_system()

    # Execute query
    logger.info(f"Executing query: {query}")
    result = rag.query(query, enable_self_correction=enable_self_correction)

    # Format response
    response_body = {
        "query": query,
        "answer": result.get("answer"),
        "status": result.get("status"),
        "num_documents": len(result.get("documents", [])),
        "attempts": result.get("attempts", 1),
    }

    if result.get("evaluation"):
        response_body["evaluation"] = {
            "overall_verdict": result["evaluation"]["overall_verdict"],
            "scores": result["evaluation"].get("quality", {}).get("scores", {})
        }

    return {
        "statusCode": 200,
        "body": json.dumps(response_body)
    }


def handle_index(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle index action - index documents from S3.

    Args:
        event: Lambda event

    Returns:
        Indexing response
    """
    bucket_name = os.environ.get("S3_BUCKET_NAME")
    s3_prefix = event.get("s3_prefix", "")
    file_pattern = event.get("file_pattern", ".txt")

    if not bucket_name:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "S3_BUCKET_NAME not configured"})
        }

    # Initialize components
    s3_loader = S3DocumentLoader(bucket_name=bucket_name)
    indexer = DocumentIndexer()

    # Load documents from S3
    logger.info(f"Loading documents from s3://{bucket_name}/{s3_prefix}")
    documents = s3_loader.load_documents(prefix=s3_prefix, suffix=file_pattern)

    if not documents:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "No documents found in S3"})
        }

    # Index documents
    logger.info(f"Indexing {len(documents)} documents...")
    total_chunks = 0
    for doc in documents:
        chunks = indexer.index_from_text(
            doc.page_content,
            metadata=doc.metadata
        )
        total_chunks += chunks

    # Upload vector store back to S3
    vector_store_prefix = os.environ.get("S3_VECTOR_STORE_PREFIX", "vector_store")
    s3_persistence = S3VectorStorePersistence(
        bucket_name=bucket_name,
        s3_prefix=vector_store_prefix,
        local_path=indexer.settings.vector_store_path
    )

    logger.info("Uploading vector store to S3...")
    s3_persistence.sync_to_s3()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Indexing completed successfully",
            "documents_loaded": len(documents),
            "chunks_indexed": total_chunks,
            "s3_bucket": bucket_name,
            "s3_prefix": s3_prefix
        })
    }


def handle_stats() -> Dict[str, Any]:
    """Handle stats action.

    Returns:
        Statistics response
    """
    rag = initialize_rag_system()
    indexer = DocumentIndexer()

    stats = indexer.get_collection_stats()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "collection_stats": stats
        })
    }

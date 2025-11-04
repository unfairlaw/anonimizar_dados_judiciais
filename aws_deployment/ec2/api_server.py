"""FastAPI server for RAG system on EC2."""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from rag_ecosystem.agents.agentic_rag import AgenticRAG
from rag_ecosystem.components.s3_loader import S3DocumentLoader
from rag_ecosystem.components.s3_vector_store import S3VectorStorePersistence
from rag_ecosystem.components.indexing import DocumentIndexer
from rag_ecosystem.config.settings import get_settings
from rag_ecosystem.utils.logger import setup_logger

# Initialize
app = FastAPI(title="RAG Ecosystem API", version="1.0.0")
logger = setup_logger("api_server")

# Global RAG system (initialized on startup)
rag_system: Optional[AgenticRAG] = None
s3_persistence: Optional[S3VectorStorePersistence] = None


class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    enable_self_correction: bool = True


class QueryResponse(BaseModel):
    """Query response model."""
    query: str
    answer: str
    status: str
    num_documents: int
    attempts: int
    evaluation: Optional[dict] = None


class IndexRequest(BaseModel):
    """Index request model."""
    s3_prefix: str = ""
    file_pattern: str = ".txt"
    clear_existing: bool = False


class IndexResponse(BaseModel):
    """Index response model."""
    message: str
    documents_loaded: int
    chunks_indexed: int


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup."""
    global rag_system, s3_persistence

    logger.info("Initializing RAG system...")

    # Get configuration
    bucket_name = os.environ.get("S3_BUCKET_NAME")
    if not bucket_name:
        logger.warning("S3_BUCKET_NAME not set, S3 sync disabled")
    else:
        # Setup S3 persistence
        s3_persistence = S3VectorStorePersistence(
            bucket_name=bucket_name,
            s3_prefix=os.environ.get("S3_VECTOR_STORE_PREFIX", "vector_store"),
        )

        # Sync from S3
        logger.info("Syncing vector store from S3...")
        s3_persistence.sync_from_s3()

    # Initialize RAG system
    rag_system = AgenticRAG()
    logger.info("RAG system initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Sync vector store to S3 on shutdown."""
    if s3_persistence:
        logger.info("Syncing vector store to S3...")
        s3_persistence.sync_to_s3()
        logger.info("Sync completed")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "rag_initialized": rag_system is not None,
        "s3_enabled": s3_persistence is not None
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system.

    Args:
        request: Query request

    Returns:
        Query response
    """
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    try:
        logger.info(f"Processing query: {request.query}")

        result = rag_system.query(
            request.query,
            enable_self_correction=request.enable_self_correction
        )

        response = QueryResponse(
            query=request.query,
            answer=result.get("answer", ""),
            status=result.get("status", "unknown"),
            num_documents=len(result.get("documents", [])),
            attempts=result.get("attempts", 1),
        )

        if result.get("evaluation"):
            response.evaluation = {
                "overall_verdict": result["evaluation"]["overall_verdict"],
                "scores": result["evaluation"].get("quality", {}).get("scores", {})
            }

        return response

    except Exception as e:
        logger.exception("Error processing query")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index", response_model=IndexResponse)
async def index_documents(request: IndexRequest):
    """Index documents from S3.

    Args:
        request: Index request

    Returns:
        Index response
    """
    bucket_name = os.environ.get("S3_BUCKET_NAME")
    if not bucket_name:
        raise HTTPException(
            status_code=400,
            detail="S3_BUCKET_NAME not configured"
        )

    try:
        # Load from S3
        s3_loader = S3DocumentLoader(bucket_name=bucket_name)
        logger.info(f"Loading documents from s3://{bucket_name}/{request.s3_prefix}")

        documents = s3_loader.load_documents(
            prefix=request.s3_prefix,
            suffix=request.file_pattern
        )

        if not documents:
            raise HTTPException(status_code=404, detail="No documents found")

        # Index documents
        indexer = DocumentIndexer()

        if request.clear_existing:
            logger.info("Clearing existing collection...")
            indexer.clear_collection()

        total_chunks = 0
        for doc in documents:
            chunks = indexer.index_from_text(
                doc.page_content,
                metadata=doc.metadata
            )
            total_chunks += chunks

        # Sync to S3
        if s3_persistence:
            logger.info("Syncing vector store to S3...")
            s3_persistence.sync_to_s3()

        return IndexResponse(
            message="Indexing completed successfully",
            documents_loaded=len(documents),
            chunks_indexed=total_chunks
        )

    except Exception as e:
        logger.exception("Error indexing documents")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get collection statistics."""
    try:
        indexer = DocumentIndexer()
        stats = indexer.get_collection_stats()
        return {"collection_stats": stats}

    except Exception as e:
        logger.exception("Error getting stats")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync/download")
async def sync_download():
    """Download vector store from S3."""
    if not s3_persistence:
        raise HTTPException(status_code=400, detail="S3 sync not configured")

    try:
        success = s3_persistence.sync_from_s3()
        return {
            "message": "Sync completed" if success else "No vector store found in S3",
            "success": success
        }
    except Exception as e:
        logger.exception("Error syncing from S3")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync/upload")
async def sync_upload():
    """Upload vector store to S3."""
    if not s3_persistence:
        raise HTTPException(status_code=400, detail="S3 sync not configured")

    try:
        success = s3_persistence.sync_to_s3()
        return {
            "message": "Upload completed successfully",
            "success": success
        }
    except Exception as e:
        logger.exception("Error syncing to S3")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run with: python api_server.py
    # Production: gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app
    uvicorn.run(app, host="0.0.0.0", port=8000)

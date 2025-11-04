"""AWS Bedrock embeddings integration."""

import json
import boto3
from typing import List, Optional, Any
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field
from rag_ecosystem.utils.logger import setup_logger

logger = setup_logger("bedrock_embeddings")


class BedrockEmbeddings(BaseModel, Embeddings):
    """AWS Bedrock embeddings wrapper."""

    model_id: str = Field(default="amazon.titan-embed-text-v1")
    region_name: str = Field(default="us-east-1")
    normalize: bool = Field(default=True)

    bedrock_client: Any = Field(default=None, exclude=True)

    class Config:
        """Configuration for this pydantic object."""
        extra = "forbid"
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        """Initialize Bedrock embeddings."""
        super().__init__(**kwargs)

        # Initialize Bedrock client
        if self.bedrock_client is None:
            self.bedrock_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=self.region_name
            )

        logger.info(f"Initialized Bedrock Embeddings with model: {self.model_id}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        embeddings = []

        for text in texts:
            embedding = self._embed_text(text)
            embeddings.append(embedding)

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a query text.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        return self._embed_text(text)

    def _embed_text(self, text: str) -> List[float]:
        """Embed a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            # Prepare request based on model
            if "amazon.titan-embed" in self.model_id:
                body = {
                    "inputText": text,
                }
                if self.normalize:
                    body["normalize"] = True

            elif "cohere.embed" in self.model_id:
                body = {
                    "texts": [text],
                    "input_type": "search_document",
                    "truncate": "END"
                }
            else:
                raise ValueError(f"Unsupported embedding model: {self.model_id}")

            # Invoke model
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )

            # Parse response
            response_body = json.loads(response["body"].read())

            # Extract embedding based on model
            if "amazon.titan-embed" in self.model_id:
                embedding = response_body.get("embedding", [])
            elif "cohere.embed" in self.model_id:
                embedding = response_body.get("embeddings", [[]])[0]
            else:
                embedding = []

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise


def get_bedrock_embeddings(
    model_id: str = "amazon.titan-embed-text-v1",
    region_name: str = "us-east-1",
    normalize: bool = True,
) -> BedrockEmbeddings:
    """Create a Bedrock embeddings instance.

    Args:
        model_id: Bedrock embedding model ID
        region_name: AWS region
        normalize: Whether to normalize embeddings

    Returns:
        BedrockEmbeddings instance
    """
    return BedrockEmbeddings(
        model_id=model_id,
        region_name=region_name,
        normalize=normalize,
    )

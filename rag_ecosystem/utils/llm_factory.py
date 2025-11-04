"""Factory for creating LLM and embedding instances."""

from typing import Optional, Any
from langchain_core.language_models import BaseLLM
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings

from rag_ecosystem.config.settings import get_settings
from rag_ecosystem.components.bedrock_llm import BedrockLLM
from rag_ecosystem.components.bedrock_embeddings import BedrockEmbeddings
from rag_ecosystem.utils.logger import setup_logger

logger = setup_logger("llm_factory")


def create_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> BaseLLM:
    """Create an LLM instance based on provider.

    Args:
        provider: LLM provider (bedrock, openai, anthropic, ollama)
        model: Model identifier
        temperature: Generation temperature
        max_tokens: Maximum tokens to generate

    Returns:
        LLM instance
    """
    settings = get_settings()

    # Use settings defaults if not specified
    provider = provider or settings.llm_provider
    temperature = temperature if temperature is not None else settings.llm_temperature
    max_tokens = max_tokens or settings.llm_max_tokens

    logger.info(f"Creating LLM with provider: {provider}")

    if provider == "bedrock":
        model = model or settings.bedrock_llm_model
        return BedrockLLM(
            model_id=model,
            region_name=settings.bedrock_region,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    elif provider == "openai":
        model = model or settings.llm_model
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=settings.openai_api_key,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        model = model or settings.llm_model
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=settings.anthropic_api_key,
        )

    elif provider == "ollama":
        from langchain_community.llms import Ollama
        model = model or settings.llm_model
        return Ollama(
            model=model,
            temperature=temperature,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def create_embeddings(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> Embeddings:
    """Create an embeddings instance based on provider.

    Args:
        provider: Embeddings provider (bedrock, huggingface, openai)
        model: Model identifier

    Returns:
        Embeddings instance
    """
    settings = get_settings()

    # Use settings defaults if not specified
    provider = provider or settings.embedding_provider
    model = model or settings.embedding_model

    logger.info(f"Creating embeddings with provider: {provider}, model: {model}")

    if provider == "bedrock":
        return BedrockEmbeddings(
            model_id=model,
            region_name=settings.bedrock_region,
        )

    elif provider == "huggingface":
        return HuggingFaceEmbeddings(
            model_name=model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    elif provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=model,
            api_key=settings.openai_api_key,
        )

    else:
        raise ValueError(f"Unsupported embeddings provider: {provider}")

"""
RAG Knowledge API Main Application Module

This module initializes and configures the FastAPI application for the RAG backend.
It sets up CORS middleware, loads configuration and data, and wires together the
Gemini-based Router, Retriever, and Responder components into a chat endpoint.
"""

import pandas as pd
import structlog
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient

from flare_ai_rag.ai import GeminiEmbedding, GeminiProvider
from flare_ai_rag.api import ChatRouter
from flare_ai_rag.attestation import Vtpm
from flare_ai_rag.prompts import PromptService
from flare_ai_rag.responder import GeminiResponder, ResponderConfig
from flare_ai_rag.retriever import QdrantRetriever, RetrieverConfig, generate_collection
from flare_ai_rag.router import GeminiRouter, RouterConfig
from flare_ai_rag.settings import settings
from flare_ai_rag.utils import load_json

logger = structlog.get_logger(__name__)


def setup_router(input_config: dict) -> tuple[GeminiProvider, GeminiRouter]:
    """Initialize a Gemini Provider for routing."""
    # Setup router config
    router_model_config = input_config["router_model"]
    router_config = RouterConfig.load(router_model_config)

    # Setup Gemini client based on Router config
    # Older version used a system_instruction
    gemini_provider = GeminiProvider(
        api_key=settings.gemini_api_key, model=router_config.model.model_id
    )
    gemini_router = GeminiRouter(client=gemini_provider, config=router_config)

    return gemini_provider, gemini_router


def setup_retriever(
    qdrant_client: QdrantClient,
    input_config: dict,
    df_docs: pd.DataFrame,
) -> QdrantRetriever:
    """Initialize the Qdrant retriever."""
    # Set up Qdrant config
    retriever_config = RetrieverConfig.load(input_config["retriever_config"])

    # Set up Gemini Embedding client
    embedding_client = GeminiEmbedding(settings.gemini_api_key)
    # (Re)generate qdrant collection
    generate_collection(
        df_docs,
        qdrant_client,
        retriever_config,
        embedding_client=embedding_client,
    )
    logger.info(
        "The Qdrant collection has been generated.",
        collection_name=retriever_config.collection_name,
    )
    # Return retriever
    return QdrantRetriever(
        client=qdrant_client,
        retriever_config=retriever_config,
        embedding_client=embedding_client,
    )


def setup_qdrant(input_config: dict) -> QdrantClient:
    """Initialize Qdrant client."""
    logger.info("Setting up Qdrant client...")
    retriever_config = RetrieverConfig.load(input_config["retriever_config"])
    qdrant_client = QdrantClient(host=retriever_config.host, port=retriever_config.port)
    logger.info("Qdrant client has been set up.")

    return qdrant_client


def setup_responder(input_config: dict) -> GeminiResponder:
    """Initialize the responder."""
    # Set up Responder Config.
    responder_config = input_config["responder_model"]
    responder_config = ResponderConfig.load(responder_config)

    # Set up a new Gemini Provider based on Responder Config.
    gemini_provider = GeminiProvider(
        api_key=settings.gemini_api_key,
        model=responder_config.model.model_id,
        system_instruction=responder_config.system_prompt,
    )
    return GeminiResponder(client=gemini_provider, responder_config=responder_config)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    This function:
      1. Creates a new FastAPI instance with optional CORS middleware.
      2. Loads configuration.
      3. Sets up the Gemini Router, Qdrant Retriever, and Gemini Responder.
      4. Loads RAG data and (re)generates the Qdrant collection.
      5. Initializes a ChatRouter that wraps the RAG pipeline.
      6. Registers the chat endpoint under the /chat prefix.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    app = FastAPI(title="RAG Knowledge API", version="1.0", redirect_slashes=False)

    # Optional: configure CORS middleware using settings.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Load input configuration.
    input_config = load_json(settings.input_path / "input_parameters.json")

    # Load RAG data.
    df_docs = pd.read_csv(settings.data_path / "docs.csv", delimiter=",")
    logger.info("Loaded CSV Data.", num_rows=len(df_docs))

    # Set up the RAG components: 1. Gemini Provider
    base_ai, router_component = setup_router(input_config)

    # 2a. Set up Qdrant client.
    qdrant_client = setup_qdrant(input_config)

    # 2b. Set up the Retriever.
    retriever_component = setup_retriever(qdrant_client, input_config, df_docs)

    # 3. Set up the Responder.
    responder_component = setup_responder(input_config)

    # Create an APIRouter for chat endpoints and initialize ChatRouter.
    chat_router = ChatRouter(
        router=APIRouter(),
        ai=base_ai,
        query_router=router_component,
        retriever=retriever_component,
        responder=responder_component,
        attestation=Vtpm(simulate=settings.simulate_attestation),
        prompts=PromptService(),
    )
    app.include_router(chat_router.router, prefix="/api/routes/chat", tags=["chat"])

    return app


app = create_app()


def start() -> None:
    """
    Start the FastAPI application server.
    """
    uvicorn.run(app, host="0.0.0.0", port=8080)  # noqa: S104


if __name__ == "__main__":
    start()

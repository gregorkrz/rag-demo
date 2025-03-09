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

MODELS = ["gemini-1.5-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash-8b"]

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


def create_routers_for_each_model() -> FastAPI:
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

    result = {}
    # Load input configuration.
    df_docs = pd.read_csv(settings.data_path / "covidds.csv", delimiter=",")
    logger.info("Loaded CSV Data.", num_rows=len(df_docs))
    for i, model in enumerate(MODELS):
        input_config = load_json(settings.input_path / "input_parameters.json")
        input_config["retriever_config"]["collection_name"] = f"pubmed_collection"
        input_config["router_model"]["id"] = model
        input_config["responder_model"]["id"] = model
        base_ai, router_component = setup_router(input_config)
        qdrant_client = setup_qdrant(input_config)
        retriever_component = setup_retriever(qdrant_client, input_config, df_docs)
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
        result[model] = chat_router
        #app.include_router(chat_router.router, prefix="/api/routes/chat/" + str(i), tags=["chat"])

    return result


routers = create_routers_for_each_model()

from src.provider import FlareProvider
from src.contract import contract_ABI, contract_address

account_addresses = {
    "gemini-1.5-flash": "0x4eF1190cA09A6692030bf6A6E1447fE8f357D440",
    "gemini-2.0-flash-lite": "0x8645962a7e3009df2F1529727422A7D62fd77660",
    "gemini-1.5-flash-8b": "0x80402995a9781E69Bb4d63D42F60C2085EE72968"
}

private_keys = {
    "gemini-1.5-flash": "465b2ae9d8bfa9ebddf57bd177de4f26309f063dd65ad2c12d268c0ada726fef",
    "gemini-2.0-flash-lite": "c5b539bf42291a1210593f2ed4529763df7f51008cf2e2b3e6407444df01c5c3",
    "gemini-1.5-flash-8b": "8d797185a8a606abcf3cbe39be40e3b3eb805b81d94571ef0c560f1fd0a97fd9"
}



providers = {}
contracts = {}

default_provider = None
default_contract = None
default_chat_router = None

for model in MODELS:
    if model in account_addresses and model in private_keys:
        print("Registering provider for model", model)
        providers[model] = FlareProvider("https://coston2-api.flare.network/ext/C/rpc")
        providers[model].private_key = private_keys[model]
        providers[model].address = account_addresses[model]
        contracts[model] = providers[model].w3.eth.contract(address=contract_address, abi=contract_ABI["abi"])
        if default_provider is None:
            default_provider = providers[model]
            print("Set the default provider (for fetching data)")
        if default_contract is None:
            default_contract = contracts[model]
            print("Set the default contract (for fetching data)")
        if default_chat_router is None:
            default_chat_router = routers[model]
            print("Set the default chat router (for processing data)")
processed_request_ids = set()
import json
async def process_text(text, request_id, provider, contract, chat_router):
    print("Processing text", text, "for request ID", request_id)
    nonce = provider.w3.eth.get_transaction_count(provider.address)
    tx = {
        'nonce': nonce,
        'value': 0,
        'gas': 2000000,
        'gasPrice': provider.w3.to_wei('50', 'gwei'),
        "from": provider.address
    }
    try:
        response = await chat_router.asyncquery(text)
        response = json.dumps(response)
    except:
        print("Exception")
        return
    result = contract.functions.submitVerification(request_id, response).build_transaction(tx)
    signed_transaction = provider.w3.eth.account.sign_transaction(result, private_key=provider.private_key)
    provider.w3.eth.send_raw_transaction(signed_transaction.raw_transaction)
    print("Sent the transaction, hope it works lol")

from time import sleep
import asyncio
def start() -> None:
    """
    Start the FastAPI application server.
    """

    #asyncio.run(process_text("COVID did 100% come from bats", 0, default_provider, default_contract, default_chat_router)) # For testing
    #sleep(15)

    while True:
        # print("Retrieving from block number", provider.w3.eth.block_number-30)
        print("Retrieving from block number", default_provider.w3.eth.block_number - 10)
        logs = default_contract.events.RequestSubmitted().get_logs(from_block=default_provider.w3.eth.block_number - 10)
        for log in logs:
            if log.args.requestId in processed_request_ids:
                continue
            processed_request_ids.add(log.args.requestId)
            for model in providers:
                provider = providers[model]
                contract = contracts[model]
                process_text(log.args.text, log.args.requestId, provider, contract, model)
        sleep(3)


if __name__ == "__main__":
    start()

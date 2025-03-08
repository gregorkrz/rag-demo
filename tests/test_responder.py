import structlog

from flare_ai_rag.ai import GeminiProvider, OpenRouterClient
from flare_ai_rag.responder import GeminiResponder, OpenRouterResponder, ResponderConfig
from flare_ai_rag.settings import settings

logger = structlog.get_logger(__name__)


def test_gemini_responder(query: str, retrieved_docs: list[dict]) -> None:
    # Set up Responder Config.
    responder_config = ResponderConfig.load({"id": "gemini-1.5-flash"})

    # Set up a new Gemini Provider based on Responder Config.
    gemini_provider = GeminiProvider(
        api_key=settings.gemini_api_key,
        model=responder_config.model.model_id,
        system_instruction=responder_config.system_prompt,
    )

    # Set up Gemini Responder
    responder = GeminiResponder(
        client=gemini_provider, responder_config=responder_config
    )

    # Get answer
    answer = responder.generate_response(query, retrieved_docs)
    logger.info("Answer provided.", answer=answer)


def test_openrouter_responder(query: str, retrieved_docs: list[dict]) -> None:
    # Initialize OpenRouter client
    client = OpenRouterClient(
        api_key=settings.open_router_api_key, base_url=settings.open_router_base_url
    )

    # Set up responder config
    model_config = {
        "id": "deepseek/deepseek-chat:free",
        "max_tokens": 200,
        "temperature": 0,
    }
    responder_config = ResponderConfig.load(model_config)

    # Set up the Responder
    responder = OpenRouterResponder(client=client, responder_config=responder_config)

    # Get answer
    answer = responder.generate_response(query, retrieved_docs)
    logger.info("Answer provided.", answer=answer)


def main() -> None:
    query = "What is Flare?"

    # Mock retrieved documents
    retrieved_docs = [
        {
            "text": (
                "Flare is the blockchain for data ☀️**, offering developers and users "
                "secure, decentralized access to high-integrity data from other "
                "chains and the internet."
            ),
            "metadata": {"filename": "1-intro.mdx"},
        },
        {
            "text": (
                "Flare's Layer-1 network uniquely supports enshrined data protocols "
                "at the network layer, making it the only EVM-compatible smart "
                "contract platform optimized for decentralized data acquisition, "
                "including price and time-series data, blockchain event and state "
                "data, and Web2 API data.",
            ),
            "metadata": {"filename": "details.mdx"},
        },
    ]

    # For Open Router: test_openrouter_responder(query, retrieved_docs)
    test_gemini_responder(query, retrieved_docs)


if __name__ == "__main__":
    main()

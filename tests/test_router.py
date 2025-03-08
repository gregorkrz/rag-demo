import structlog

from flare_ai_rag.ai import GeminiProvider, OpenRouterClient
from flare_ai_rag.router import GeminiRouter, QueryRouter, RouterConfig
from flare_ai_rag.settings import settings

logger = structlog.get_logger(__name__)


def test_open_router(queries: list[str]) -> None:
    # Initialize OpenRouter client
    client = OpenRouterClient(
        api_key=settings.open_router_api_key, base_url=settings.open_router_base_url
    )

    # Set up router config
    model_config = {"id": "qwen/qwen-vl-plus:free", "max_tokens": 50, "temperature": 0}
    router_config = RouterConfig.load(model_config)

    # Initialize the QueryRouter.
    router = QueryRouter(client=client, config=router_config)

    # Process each query and print its classification.
    for query in queries:
        classification = router.route_query(query)
        logger.info("Query processed.", classification=classification)


def test_gemini_router(queries: list[str]) -> None:
    router_config = RouterConfig.load({"id": "gemini-1.5-flash"})

    # Initialize Gemini client
    client = GeminiProvider(
        api_key=settings.gemini_api_key,
        model=router_config.model.model_id,
        system_instruction=router_config.system_prompt,
    )
    logger.info("Initialized Gemini Provider.")
    # Initialize the GeminiRouter
    router = GeminiRouter(client=client, config=router_config)

    # Process each query and print its classification.
    for query in queries:
        classification = router.route_query(query)
        logger.info("Query processed.", classification=classification)


def main() -> None:
    queries = [
        "What is the capital of France?",
        "Is Flare an EVM chain?",
        "What is the FTSO?",
    ]

    test_gemini_router(queries)

    # For OpenRouter: test_open_router(queries)


if __name__ == "__main__":
    main()

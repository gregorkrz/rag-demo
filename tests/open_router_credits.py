import structlog

from flare_ai_rag.ai import OpenRouterClient
from flare_ai_rag.settings import settings

logger = structlog.get_logger(__name__)


def get_credits(provider: OpenRouterClient) -> None:
    """Retrieve available OpenRouter credits."""
    current_credits = provider.get_credits()
    logger.info("current credits", current_credits=current_credits)


if __name__ == "__main__":
    # Initialize the OpenRouter client.
    provider = OpenRouterClient(
        api_key=settings.open_router_api_key,
        base_url=settings.open_router_base_url,
    )

    get_credits(provider)

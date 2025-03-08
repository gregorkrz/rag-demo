from typing import Any, override

import structlog

from flare_ai_rag.ai import GeminiProvider, OpenRouterClient
from flare_ai_rag.router import BaseQueryRouter
from flare_ai_rag.router.config import RouterConfig
from flare_ai_rag.utils import (
    parse_chat_response_as_json,
    parse_gemini_response_as_json,
)

logger = structlog.get_logger(__name__)


class GeminiRouter(BaseQueryRouter):
    """
    A simple query router that uses GCloud's Gemini
    to classify a query as ANSWER, CLARIFY, or REJECT.
    """

    def __init__(self, client: GeminiProvider, config: RouterConfig) -> None:
        """
        Initialize the router with a GeminiProvider instance.
        """
        self.router_config = config
        self.client = client

    @override
    def route_query(
        self,
        prompt: str,
        response_mime_type: str | None = None,
        response_schema: Any | None = None,
    ) -> str:
        """
        Analyze the query using the configured prompt and classify it.
        """
        logger.debug("Sending prompt...", prompt=prompt)
        # Use the generate method of GeminiProvider to obtain a response.
        response = self.client.generate(
            prompt=prompt,
            response_mime_type=response_mime_type,
            response_schema=response_schema,
        )
        # Parse the response to extract classification.
        classification = (
            parse_gemini_response_as_json(response.raw_response)
            .get("classification", "")
            .upper()
        )
        # Validate the classification.
        valid_options = {
            self.router_config.answer_option,
            self.router_config.clarify_option,
            self.router_config.reject_option,
        }
        if classification not in valid_options:
            classification = self.router_config.clarify_option

        return classification


class QueryRouter(BaseQueryRouter):
    """
    A simple query router that uses OpenRouter's chat completion endpoint to
    classify a query as ANSWER, CLARIFY, or REJECT.
    """

    def __init__(self, client: OpenRouterClient, config: RouterConfig) -> None:
        """
        Initialize the router with an API key and model name.
        :param api_key: Your OpenRouter API key.
        :param model: The model to use.
        """
        self.router_config = config
        self.client = client
        self.query = ""

    @override
    def route_query(
        self,
        prompt: str,
        response_mime_type: str | None = None,
        response_schema: Any | None = None,
    ) -> str:
        """
        Analyze the query using the configured prompt and classify it.

        :param query: The user query.
        :return: One of the classification options defined in the config.

        """
        payload: dict[str, Any] = {
            "model": self.router_config.model.model_id,
            "messages": [
                {"role": "system", "content": self.router_config.system_prompt},
                {"role": "user", "content": prompt},
            ],
        }

        if self.router_config.model.max_tokens is not None:
            payload["max_tokens"] = self.router_config.model.max_tokens
        if self.router_config.model.temperature is not None:
            payload["temperature"] = self.router_config.model.temperature

        # Get response
        response = self.client.send_chat_completion(payload)
        classification = (
            parse_chat_response_as_json(response).get("classification", "").upper()
        )

        # Validate the classification.
        valid_options = {
            self.router_config.answer_option,
            self.router_config.clarify_option,
            self.router_config.reject_option,
        }
        if classification not in valid_options:
            classification = self.router_config.clarify_option

        return classification

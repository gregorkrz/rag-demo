import json
import re
from typing import Any

from flare_ai_rag.ai.base import ModelResponse


def parse_chat_response(response: dict) -> str:
    """Parse response from chat completion endpoint"""
    return response.get("choices", [])[0].get("message", {}).get("content", "")


def extract_author(model_id: str) -> tuple[str, str]:
    """
    Extract the author and slug from a model_id.

    :param model_id: The model ID string.
    :return: A tuple (author, slug).
    """
    author, slug = model_id.split("/", 1)
    return author, slug


def parse_chat_response_as_json(response: dict) -> dict[str, Any]:
    """Parse response from OpenRouter's chat completion endpoint"""
    json_data = parse_chat_response(response)
    return json.loads(json_data)


def parse_gemini_response_as_json(raw_response: ModelResponse) -> dict[str, Any]:
    """
    Extracts JSON content from a Gemini response.

    Args:
        raw_response (ModelResponse): The raw response from Gemini.

    Returns:
        dict: The parsed JSON content.
    """
    text = raw_response.text
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    json_str = match.group(1) if match else text
    return json.loads(json_str)

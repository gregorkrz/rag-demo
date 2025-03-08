"""
Schema Definitions for Flare AI RAG Prompts

This module defines the core data structures and types used for managing prompts
and their responses in the Flare AI RAG system.

The module provides type safety and structured data handling for AI prompt
interactions, ensuring consistency in prompt formatting and response handling
across the application.
"""

from dataclasses import dataclass
from enum import Enum
from string import Template
from typing import TypedDict


class SemanticRouterResponse(str, Enum):
    """
    Enumeration of possible semantic routing outcomes for user queries.

    This enum defines the various types of operations that can be triggered
    based on user input analysis. Each value represents a specific action
    or response type that the system can handle.

    Attributes:
        REQUEST_ATTESTATION: Route to attestation request handling
        CONVERSATIONAL: Route to general conversational response
        RAG_ROUTER: Router to RAG pipeline router
        RAG_RESPONDER: Router to RAG pipeline responder
    """

    REQUEST_ATTESTATION = "RequestAttestation"
    CONVERSATIONAL = "Conversational"
    RAG_ROUTER = "RagRouter"
    RAG_RESPONDER = "RagResponder"


class RAGRouterResponse(TypedDict):
    """
    Type definition for RAG router response type.

    Defines the required fields for a RAG routing operation,

    Attributes:
        classification (str): The response class
    """

    classification: str


class PromptInputs(TypedDict, total=False):
    """
    Type definition for various types of prompt inputs.

    A flexible TypedDict that defines possible input types for prompts.
    The total=False flag indicates that all fields are optional.

    Attributes:
        user_input (str): Raw user input text
        text (str): Processed or formatted text
        content (str): General content string
        code (str): Code snippet or related content
    """

    user_input: str
    text: str
    content: str
    code: str


@dataclass
class Prompt:
    """
    A dataclass representing an AI prompt template with its metadata
    and formatting logic.

    This class encapsulates all information needed to define and use an AI prompt,
    including its template text, required inputs, response handling, and metadata.

    Attributes:
        name (str): Unique identifier for the prompt
        description (str): Human-readable description of the prompt's purpose
        template (str): The prompt template text with optional placeholder variables
        required_inputs (list[str] | None): List of required input variable names
        response_schema (type | None): Expected response type/schema
        response_mime_type (str | None): MIME type of the expected response
        examples (list[dict[str, str]] | None): Example usages of the prompt
        category (str | None): Grouping category for the prompt
        version (str): Version string for the prompt template

    Example:
        ```python
        prompt = Prompt(
            name="token_send",
            description="Format a token send request",
            template="Send ${amount} tokens to ${address}",
            required_inputs=["amount", "address"],
            response_schema=TokenSendResponse,
            response_mime_type="application/json",
        )
        formatted = prompt.format(amount="100", address="0x123...")
        ```
    """

    name: str
    description: str
    template: str
    required_inputs: list[str] | None
    response_schema: type | None
    response_mime_type: str | None
    examples: list[dict[str, str]] | None = None
    category: str | None = None
    version: str = "1.0"

    def format(self, **kwargs: str | PromptInputs) -> str:
        """
        Format the prompt template with provided input values.

        This method uses string.Template to substitute variables in the prompt
        template with provided values. It validates that all required inputs
        are provided before formatting.

        Args:
            **kwargs: Keyword arguments containing values for template variables.
                     Can be strings or PromptInputs objects.

        Returns:
            str: The formatted prompt string with all variables substituted.

        Raises:
            ValueError: If any required inputs are missing from kwargs.
            KeyError: If template substitution fails due to missing keys.

        Example:
            ```python
            prompt = Prompt(
                template="Hello ${name}!",
                required_inputs=["name"],
                ...
            )
            result = prompt.format(name="Alice")
            ```
        """
        if not self.required_inputs:
            return self.template

        try:
            return Template(self.template).safe_substitute(**kwargs)
        except KeyError as e:
            missing_keys = set(self.required_inputs) - set(kwargs.keys())
            if missing_keys:
                msg = f"Missing required inputs: {missing_keys}"
                raise ValueError(msg) from e
            raise

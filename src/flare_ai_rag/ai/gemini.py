"""
Gemini AI Provider Module

This module implements the Gemini AI provider for the AI Agent API, integrating
with Google's Generative AI service. It handles chat sessions, content generation,
and message management while maintaining a consistent AI personality.
"""

from typing import Any, override

import structlog
from google.generativeai.client import configure
from google.generativeai.embedding import (
    EmbeddingTaskType,
)
from google.generativeai.embedding import (
    embed_content as _embed_content,
)
from google.generativeai.generative_models import ChatSession, GenerativeModel
from google.generativeai.types import GenerationConfig

from flare_ai_rag.ai.base import BaseAIProvider, ModelResponse

logger = structlog.get_logger(__name__)


SYSTEM_INSTRUCTION = """
You are an AI assistant specialized in helping users navigate
the Flare blockchain documentation.

When helping users:
- Prioritize security best practices
- Verify user understanding of important steps
- Format technical information (addresses, hashes, etc.) in easily readable ways

You maintain professionalism while allowing your subtle wit to make interactions
more engaging - your goal is to be helpful first, entertaining second.
"""


class GeminiProvider(BaseAIProvider):
    """
    Provider class for Google's Gemini AI service.

    This class implements the BaseAIProvider interface to provide AI capabilities
    through Google's Gemini models. It manages chat sessions, generates content,
    and maintains conversation history.

    Attributes:
        chat (generativeai.ChatSession | None): Active chat session
        model (generativeai.GenerativeModel): Configured Gemini model instance
        chat_history: History of chat interactions
        logger (BoundLogger): Structured logger for the provider
    """

    def __init__(self, api_key: str, model: str, **kwargs: str) -> None:
        """
        Initialize the Gemini provider with API credentials and model configuration.

        Args:
            api_key (str): Google API key for authentication
            model (str): Gemini model identifier to use
            **kwargs (str): Additional configuration parameters including:
                - system_instruction: Custom system prompt for the AI personality
        """
        configure(api_key=api_key)
        self.chat: ChatSession | None = None
        self.model = GenerativeModel(
            model_name=model,
            system_instruction=kwargs.get("system_instruction", SYSTEM_INSTRUCTION),
        )
        self.chat_history = []
        self.logger = logger.bind(service="gemini")

    @override
    def reset(self) -> None:
        """
        Reset the provider state.

        Clears chat history and terminates active chat session.
        """
        self.chat_history = []
        self.chat = None
        self.logger.debug(
            "reset_gemini", chat=self.chat, chat_history=self.chat_history
        )

    @override
    def reset_model(self, model: str, **kwargs: str) -> None:
        """
        Completely reinitialize the generative model with new parameters,
        and reset the chat session and history.

        Args:
            model (str): New model identifier.
            **kwargs: Additional configuration parameters, e.g.:
                system_instruction: new system prompt.
        """
        new_system_instruction = kwargs.get("system_instruction", SYSTEM_INSTRUCTION)
        # Reinitialize the generative model.
        self.model = GenerativeModel(
            model_name=model,
            system_instruction=new_system_instruction,
        )
        # Reset chat session and history with the new system instruction.
        self.chat = None
        self.chat_history = [{"role": "system", "content": new_system_instruction}]
        self.logger.debug(
            "reset_model", model=model, system_instruction=new_system_instruction
        )

    @override
    def generate(
        self,
        prompt: str,
        response_mime_type: str | None = None,
        response_schema: Any | None = None,
    ) -> ModelResponse:
        """
        Generate content using the Gemini model.

        Args:
            prompt (str): Input prompt for content generation
            response_mime_type (str | None): Expected MIME type for the response
            response_schema (Any | None): Schema defining the response structure

        Returns:
            ModelResponse: Generated content with metadata including:
                - text: Generated text content
                - raw_response: Complete Gemini response object
                - metadata: Additional response information including:
                    - candidate_count: Number of generated candidates
                    - prompt_feedback: Feedback on the input prompt
        """
        response = self.model.generate_content(
            prompt,
            generation_config=GenerationConfig(
                response_mime_type=response_mime_type, response_schema=response_schema
            ),
        )
        self.logger.debug("generate", prompt=prompt, response_text=response.text)
        return ModelResponse(
            text=response.text,
            raw_response=response,
            metadata={
                "candidate_count": len(response.candidates),
                "prompt_feedback": response.prompt_feedback,
            },
        )

    @override
    def send_message(
        self,
        msg: str,
    ) -> ModelResponse:
        """
        Send a message in a chat session and get the response.

        Initializes a new chat session if none exists, using the current chat history.

        Args:
            msg (str): Message to send to the chat session

        Returns:
            ModelResponse: Response from the chat session including:
                - text: Generated response text
                - raw_response: Complete Gemini response object
                - metadata: Additional response information including:
                    - candidate_count: Number of generated candidates
                    - prompt_feedback: Feedback on the input message
        """
        if not self.chat:
            self.chat = self.model.start_chat(history=self.chat_history)
        response = self.chat.send_message(msg)
        self.logger.debug("send_message", msg=msg, response_text=response.text)
        return ModelResponse(
            text=response.text,
            raw_response=response,
            metadata={
                "candidate_count": len(response.candidates),
                "prompt_feedback": response.prompt_feedback,
            },
        )


class GeminiEmbedding:
    def __init__(self, api_key: str) -> None:
        """
        Initialize Gemini with API credentials.
        This client uses google.generativeai

        Args:
            api_key (str): Google API key for authentication
        """
        configure(api_key=api_key)

    def embed_content(
        self,
        embedding_model: str,
        contents: str,
        task_type: EmbeddingTaskType,
        title: str | None = None,
    ) -> list[float]:
        """
        Generate text embeddings using Gemini.

        Args:
            model (str): The embedding model to use (e.g., "text-embedding-004").
            contents (str): The text to be embedded.

        Returns:
            list[float]: The generated embedding vector.
        """
        response = _embed_content(
            model=embedding_model, content=contents, task_type=task_type, title=title
        )
        try:
            embedding = response["embedding"]
        except (KeyError, IndexError) as e:
            msg = "Failed to extract embedding from response."
            raise ValueError(msg) from e
        return embedding

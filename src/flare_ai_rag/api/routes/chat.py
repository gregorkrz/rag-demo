import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from flare_ai_rag.ai import GeminiProvider
from flare_ai_rag.attestation import Vtpm, VtpmAttestationError
from flare_ai_rag.prompts import PromptService, SemanticRouterResponse
from flare_ai_rag.responder import GeminiResponder
from flare_ai_rag.retriever import QdrantRetriever
from flare_ai_rag.router import GeminiRouter

logger = structlog.get_logger(__name__)
router = APIRouter()
import json
from fastapi.responses import JSONResponse


class ChatMessage(BaseModel):
    """
    Pydantic model for chat message validation.

    Attributes:
        message (str): The chat message content, must not be empty
    """

    message: str = Field(..., min_length=1)


class ChatRouter:
    """
    A simple chat router that processes incoming messages using the RAG pipeline.

    It wraps the existing query classification, document retrieval, and response
    generation components to handle a conversation in a single endpoint.
    """

    def __init__(  # noqa: PLR0913
        self,
        router: APIRouter,
        ai: GeminiProvider,
        query_router: GeminiRouter,
        retriever: QdrantRetriever,
        responder: GeminiResponder,
        attestation: Vtpm,
        prompts: PromptService,
    ) -> None:
        """
        Initialize the ChatRouter.

        Args:
            router (APIRouter): FastAPI router to attach endpoints.
            ai (GeminiProvider): AI client used by a simple semantic router
                to determine if an attestation was requested or if RAG
                pipeline should be used.
            query_router: RAG Component that classifies the query.
            retriever: RAG Component that retrieves relevant documents.
            responder: RAG Component that generates a response.
            attestation (Vtpm): Provider for attestation services
            prompts (PromptService): Service for managing prompts
        """
        self._router = router
        self.ai = ai
        self.query_router = query_router
        self.retriever = retriever
        self.responder = responder
        self.attestation = attestation
        self.prompts = prompts
        self.logger = logger.bind(router="chat")
        self._setup_routes()

    def _setup_routes(self) -> None:
        """
        Set up FastAPI routes for the chat endpoint.
        """

        @self._router.post("/")
        async def chat(message: ChatMessage) -> dict[str, str] | None:  # pyright: ignore [reportUnusedFunction]
            """
            Process a chat message through the RAG pipeline.
            Returns a response containing the query classification and the answer.
            """
            try:
                self.logger.debug("Received chat message", message=message.message)

                # If attestation has previously been requested:
                #if self.attestation.attestation_requested:
                #    try:
                #        resp = self.attestation.get_token([message.message])
                #    except VtpmAttestationError as e:
                #        resp = f"The attestation failed with  error:\n{e.args[0]}"
                #    self.attestation.attestation_requested = False
                #    return {"response": resp}

                route = await self.get_semantic_route(message.message)

                msg = await self.route_message(route, message.message) # Just a quick fix thing
                if msg["classification"] == "FACT_CHECK":
                    # Convert response to json
                    msg["response"] = str(msg["response"])
                return JSONResponse(content=msg)
            except Exception as e:
                self.logger.exception("Chat processing failed", error=str(e))
                raise HTTPException(status_code=500, detail=str(e)) from e

    @property
    def router(self) -> APIRouter:
        """Return the underlying FastAPI router with registered endpoints."""
        return self._router

    async def get_semantic_route(self, message: str) -> SemanticRouterResponse:
        """
        Determine the semantic route for a message using AI provider.

        Args:
            message: Message to route

        Returns:
            SemanticRouterResponse: Determined route for the message
        """
        try:
            prompt, mime_type, schema = self.prompts.get_formatted_prompt(
                "semantic_router", user_input=message
            )
            route_response = self.ai.generate(
                prompt=prompt, response_mime_type=mime_type, response_schema=schema
            )
            return SemanticRouterResponse(route_response.text)
        except Exception as e:
            self.logger.exception("routing_failed", error=str(e))
            return SemanticRouterResponse.CONVERSATIONAL

    async def route_message(
        self, route: SemanticRouterResponse, message: str
    ) -> dict[str, str]:
        """
        Route a message to the appropriate handler based on semantic route.

        Args:
            route: Determined semantic route
            message: Original message to handle

        Returns:
            dict[str, str]: Response from the appropriate handler
        """
        handlers = {
            SemanticRouterResponse.RAG_ROUTER: self.handle_rag_pipeline,
            SemanticRouterResponse.REQUEST_ATTESTATION: self.handle_attestation,
            SemanticRouterResponse.CONVERSATIONAL: self.handle_conversation,
        }
        handler = handlers.get(SemanticRouterResponse.RAG_ROUTER) # we don't really need the others
        if not handler:
            return {"response": "Unsupported route"}

        return await handler(message)

    async def handle_rag_pipeline(self, message: str) -> dict[str, str]:
        """
        Handle attestation requests.

        Args:
            _: Unused message parameter

        Returns:
            dict[str, str]: Response containing attestation request
        """
        # Step 1. Classify the user query.
        prompt, mime_type, schema = self.prompts.get_formatted_prompt("rag_router",  user_input=message)
        classification = self.query_router.route_query(
            prompt=prompt, response_mime_type=mime_type, response_schema=schema
        )
        self.logger.info("Query classified", classification=classification)

        if classification == "FACT_CHECK":
        # Step 2. Retrieve relevant documfents.
            retrieved_docs = self.retriever.semantic_search(message, top_k=5)
            self.logger.info("Documents retrieved")
            self.logger.info(retrieved_docs)

            # Step 3. Generate the final answer.
            answer = self.responder.generate_response(message, retrieved_docs)
            self.logger.info("Response generated", answer=answer)
            # if answer starts with 3 backticks and json, remove that
            if answer.startswith("```json"):
                answer_raw = answer[answer.find("\n")+1:]
                # also remove newlines and last three backticks if they are there
                if answer_raw.strip().endswith("```"):
                    answer_raw = answer_raw.strip()[:-3]
                answer_raw = answer_raw.replace("\n", " ")
            else:
                answer_raw = answer
            answer_raw = answer_raw.replace("'", '"')
            answer_raw = answer_raw.strip()
            print("answer_raw", answer_raw)
            return {"classification": classification, "response": answer,  "response_json": json.loads(answer_raw)}

        # Map static responses for CLARIFY and REJECT.
        static_responses = {
            "NOT_RELEVANT": "N/A",
            #"REJECT": "The query is out of scope.",
        }

        if classification in static_responses:
            return {
                "classification": classification,
                "response": static_responses[classification],
            }

        self.logger.exception("RAG Routing failed")
        raise ValueError(classification)

    async def handle_attestation(self, _: str) -> dict[str, str]:
        """
        Handle attestation requests.

        Args:
            _: Unused message parameter

        Returns:
            dict[str, str]: Response containing attestation request
        """
        prompt = self.prompts.get_formatted_prompt("request_attestation")[0]
        request_attestation_response = self.ai.generate(prompt=prompt)
        self.attestation.attestation_requested = True
        return {"response": request_attestation_response.text}

    async def handle_conversation(self, message: str) -> dict[str, str]:
        """
        Handle general conversation messages.

        Args:
            message: Message to process

        Returns:
            dict[str, str]: Response from AI provider
        """
        response = self.ai.send_message(message)
        return {"response": response.text}

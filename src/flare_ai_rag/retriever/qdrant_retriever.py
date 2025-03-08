from typing import override

from qdrant_client import QdrantClient

from flare_ai_rag.ai import EmbeddingTaskType, GeminiEmbedding
from flare_ai_rag.retriever.base import BaseRetriever
from flare_ai_rag.retriever.config import RetrieverConfig


class QdrantRetriever(BaseRetriever):
    def __init__(
        self,
        client: QdrantClient,
        retriever_config: RetrieverConfig,
        embedding_client: GeminiEmbedding,
    ) -> None:
        """Initialize the QdrantRetriever."""
        self.client = client
        self.retriever_config = retriever_config
        self.embedding_client = embedding_client

    @override
    def semantic_search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Perform semantic search by converting the query into a vector
        and searching in Qdrant.

        :param query: The input query.
        :param top_k: Number of top results to return.
        :return: A list of dictionaries, each representing a retrieved document.
        """
        # Convert the query into a vector embedding using Gemini
        query_vector = self.embedding_client.embed_content(
            embedding_model="models/text-embedding-004",
            contents=query,
            task_type=EmbeddingTaskType.RETRIEVAL_QUERY,
        )

        # Search Qdrant for similar vectors.
        results = self.client.search(
            collection_name=self.retriever_config.collection_name,
            query_vector=query_vector,
            limit=top_k,
        )

        # Process and return results.
        output = []
        for hit in results:
            if hit.payload:
                text = hit.payload.get("text", "")
                metadata = {
                    field: value
                    for field, value in hit.payload.items()
                    if field != "text"
                }
            else:
                text = ""
                metadata = ""
            output.append({"text": text, "score": hit.score, "metadata": metadata})
        return output

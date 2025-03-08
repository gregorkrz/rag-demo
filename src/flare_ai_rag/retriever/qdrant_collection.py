import google.api_core.exceptions
import pandas as pd
import structlog
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from flare_ai_rag.ai import EmbeddingTaskType, GeminiEmbedding
from flare_ai_rag.retriever.config import RetrieverConfig

logger = structlog.get_logger(__name__)


def _create_collection(
    client: QdrantClient, collection_name: str, vector_size: int
) -> None:
    """
    Creates a Qdrant collection with the given parameters.
    :param collection_name: Name of the collection.
    :param vector_size: Dimension of the vectors.
    """
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )


def generate_collection(
    df_docs: pd.DataFrame,
    qdrant_client: QdrantClient,
    retriever_config: RetrieverConfig,
    embedding_client: GeminiEmbedding,
) -> None:
    """Routine for generating a Qdrant collection for a specific CSV file type."""
    _create_collection(
        qdrant_client, retriever_config.collection_name, retriever_config.vector_size
    )
    logger.info(
        "Created the collection.", collection_name=retriever_config.collection_name
    )

    points = []
    for idx, (_, row) in enumerate(
        df_docs.iterrows(), start=1
    ):  # Using _ for unused variable
        content = row["Contents"]

        if not isinstance(content, str):
            logger.warning(
                "Skipping document due to missing or invalid content.",
                filename=row["Filename"],
            )
            continue

        try:
            embedding = embedding_client.embed_content(
                embedding_model=retriever_config.embedding_model,
                task_type=EmbeddingTaskType.RETRIEVAL_DOCUMENT,
                contents=content,
                title=str(row["Filename"]),
            )
        except google.api_core.exceptions.InvalidArgument as e:
            # Check if it's the known "Request payload size exceeds the limit" error
            # If so, downgrade it to a warning
            if "400 Request payload size exceeds the limit" in str(e):
                logger.warning(
                    "Skipping document due to size limit.",
                    filename=row["Filename"],
                )
                continue
            # Log the full traceback for other InvalidArgument errors
            logger.exception(
                "Error encoding document (InvalidArgument).",
                filename=row["Filename"],
            )
            continue
        except Exception:
            # Log the full traceback for any other errors
            logger.exception(
                "Error encoding document (general).",
                filename=row["Filename"],
            )
            continue

        payload = {
            "filename": row["Filename"],
            "metadata": row["Metadata"],
            "text": content,
        }

        point = PointStruct(
            id=idx,  # Using integer ID starting from 1
            vector=embedding,
            payload=payload,
        )
        points.append(point)

    if points:
        qdrant_client.upsert(
            collection_name=retriever_config.collection_name,
            points=points,
        )
        logger.info(
            "Collection generated and documents inserted into Qdrant successfully.",
            collection_name=retriever_config.collection_name,
            num_points=len(points),
        )
    else:
        logger.warning("No valid documents found to insert.")

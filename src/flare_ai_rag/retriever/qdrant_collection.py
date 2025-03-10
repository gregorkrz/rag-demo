import google.api_core.exceptions
import pandas as pd
import structlog
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from flare_ai_rag.ai import EmbeddingTaskType, GeminiEmbedding
from flare_ai_rag.retriever.config import RetrieverConfig
from qdrant_client.http.exceptions import UnexpectedResponse

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
def collection_exists(client, collection_name):
    try:
        coll = client.get_collection(collection_name)
        # If the collection exists, print the number of entries
        num_points = coll.points_count
        print("Number of points in collection:", num_points)
        return num_points > 150
    except UnexpectedResponse:
        return False

def generate_collection(
    df_docs: pd.DataFrame,
    qdrant_client: QdrantClient,
    retriever_config: RetrieverConfig,
    embedding_client: GeminiEmbedding,
) -> None:
    if collection_exists(qdrant_client, retriever_config.collection_name):
        logger.info(
            "Collection already exists.",
            collection_name=retriever_config.collection_name,
        )
        return
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
        print(idx)
        if idx >= 200:
            print("Reached the limit of 200 points (JUST FOR DEBUGGING)")
            break
        print("Row keys:", row.keys())
        content = row["content"]

        if not isinstance(content, str):
            logger.warning(
                "Skipping document due to missing or invalid content.",
                filename=row["file_name"],
            )
            continue

        try:
            embedding = embedding_client.embed_content(
                embedding_model=retriever_config.embedding_model,
                task_type=EmbeddingTaskType.RETRIEVAL_DOCUMENT,
                contents=content,
                title=str(row["file_name"]),
            )
        except google.api_core.exceptions.InvalidArgument as e:
            # Check if it's the known "Request payload size exceeds the limit" error
            # If so, downgrade it to a warning
            if "400 Request payload size exceeds the limit" in str(e):
                logger.warning(
                    "Skipping document due to size limit.",
                    filename=row["file_name"],
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
                filename=row["file_name"],
            )
            continue

        payload = {
            "filename": row["file_name"],
            "metadata": row["meta_data"],
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

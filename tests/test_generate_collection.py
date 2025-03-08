import pandas as pd
import structlog
from qdrant_client import QdrantClient

from flare_ai_rag.ai import GeminiEmbedding
from flare_ai_rag.retriever.config import RetrieverConfig
from flare_ai_rag.retriever.qdrant_collection import generate_collection
from flare_ai_rag.settings import settings
from flare_ai_rag.utils import load_json

logger = structlog.get_logger(__name__)


def main() -> None:
    # Load Qdrant config
    config_json = load_json(settings.input_path / "input_parameters.json")
    retriever_config = RetrieverConfig.load(config_json["retriever_config"])

    # Load the CSV file.
    df_docs = pd.read_csv(settings.data_path / "docs.csv", delimiter=",")
    logger.info("Loaded CSV Data.", num_rows=len(df_docs))

    # Initialize Qdrant client.
    client = QdrantClient(host=retriever_config.host, port=retriever_config.port)

    # Initialize Gemini client
    embedding_client = GeminiEmbedding(api_key=settings.gemini_api_key)

    generate_collection(
        df_docs,
        client,
        retriever_config,
        embedding_client=embedding_client,
    )


if __name__ == "__main__":
    main()

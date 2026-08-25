from typing import Tuple

from ulakbim_analysis.infrastructure.local_embedding import FastEmbedModel
from ulakbim_analysis.infrastructure.qdrant_vector_store import (
    QdrantVectorStore,
)
from ulakbim_analysis.infrastructure.vector_settings import (
    VectorExperimentSettings,
)


def create_vector_services() -> Tuple[FastEmbedModel, QdrantVectorStore]:
    settings = VectorExperimentSettings.from_env()
    embedder = FastEmbedModel(settings.embedding_model)
    store = QdrantVectorStore(
        url=settings.qdrant_url,
        collection=settings.collection,
        dimension=settings.vector_dimension,
    )
    store.check_connection()
    return embedder, store

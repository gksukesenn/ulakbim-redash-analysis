import os
from dataclasses import dataclass
from typing import Mapping, Optional

from dotenv import load_dotenv


DEFAULT_QDRANT_URL = "http://127.0.0.1:6333"
DEFAULT_COLLECTION = "ulakbim_article_similarity_experiment"
DEFAULT_EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
DEFAULT_VECTOR_DIMENSION = 384


@dataclass(frozen=True)
class VectorExperimentSettings:
    qdrant_url: str = DEFAULT_QDRANT_URL
    collection: str = DEFAULT_COLLECTION
    embedding_model: str = DEFAULT_EMBEDDING_MODEL
    vector_dimension: int = DEFAULT_VECTOR_DIMENSION

    @classmethod
    def from_env(
        cls,
        environ: Optional[Mapping[str, str]] = None,
    ) -> "VectorExperimentSettings":
        if environ is None:
            load_dotenv()
            values = os.environ
        else:
            values = environ

        dimension_text = values.get(
            "VECTOR_EXPERIMENT_DIMENSION",
            str(DEFAULT_VECTOR_DIMENSION),
        )
        try:
            dimension = int(dimension_text)
        except ValueError:
            raise ValueError("VECTOR_EXPERIMENT_DIMENSION tam sayı olmalıdır.")
        if dimension <= 0:
            raise ValueError("VECTOR_EXPERIMENT_DIMENSION pozitif olmalıdır.")

        return cls(
            qdrant_url=values.get(
                "QDRANT_URL",
                DEFAULT_QDRANT_URL,
            ).strip(),
            collection=values.get(
                "QDRANT_EXPERIMENT_COLLECTION",
                DEFAULT_COLLECTION,
            ).strip(),
            embedding_model=values.get(
                "VECTOR_EXPERIMENT_MODEL",
                DEFAULT_EMBEDDING_MODEL,
            ).strip(),
            vector_dimension=dimension,
        )

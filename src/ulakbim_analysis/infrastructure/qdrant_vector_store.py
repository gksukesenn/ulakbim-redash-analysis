from typing import List, Sequence
from uuid import NAMESPACE_URL, uuid5

from ulakbim_analysis.domain.vector_experiment import (
    SimilarityResult,
    StoredArticleVector,
    VectorPoint,
)


class QdrantVectorStore:
    def __init__(self, url: str, collection: str, dimension: int) -> None:
        try:
            from qdrant_client import QdrantClient
        except ImportError as error:
            raise RuntimeError(
                "Qdrant bağımlılığı eksik; `pip install -e '.[vector]'` "
                "komutunu çalıştırın."
            ) from error
        self._client = QdrantClient(url=url)
        self._collection = collection
        self._dimension = dimension

    def check_connection(self) -> None:
        self._client.get_collections()

    def recreate_collection(self) -> None:
        from qdrant_client.models import Distance, VectorParams

        if self._client.collection_exists(self._collection):
            self._client.delete_collection(self._collection)
        self._client.create_collection(
            collection_name=self._collection,
            vectors_config=VectorParams(
                size=self._dimension,
                distance=Distance.COSINE,
            ),
        )

    def upsert(self, points: Sequence[VectorPoint]) -> None:
        from qdrant_client.models import PointStruct

        qdrant_points = [
            PointStruct(
                id=str(uuid5(NAMESPACE_URL, point.uid)),
                vector=point.vector,
                payload=point.payload,
            )
            for point in points
        ]
        self._client.upsert(
            collection_name=self._collection,
            points=qdrant_points,
            wait=True,
        )

    def search(
        self,
        vector: Sequence[float],
        limit: int,
    ) -> List[SimilarityResult]:
        response = self._client.query_points(
            collection_name=self._collection,
            query=list(vector),
            limit=limit,
            with_payload=True,
        )
        results = []
        for point in response.points:
            payload = point.payload or {}
            results.append(
                SimilarityResult(
                    uid=str(payload.get("uid", "")),
                    score=float(point.score),
                    title=str(payload.get("title") or "Başlık yok"),
                    subjects=list(payload.get("subjects") or []),
                    group=str(payload.get("experiment_group") or ""),
                    abstract_preview=str(
                        payload.get("abstract_preview") or ""
                    ),
                )
            )
        return results

    def read_all_articles(self) -> List[StoredArticleVector]:
        """Koleksiyondaki tüm makaleleri payload ve vektörleriyle okur."""

        records = []
        offset = None
        while True:
            points, offset = self._client.scroll(
                collection_name=self._collection,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=True,
            )
            for point in points:
                payload = point.payload or {}
                vector = point.vector
                if not isinstance(vector, list):
                    raise ValueError("Qdrant point vektörü beklenen biçimde değil.")
                article_id = str(
                    payload.get("article_id") or payload.get("uid") or point.id
                )
                records.append(
                    StoredArticleVector(
                        article_id=article_id,
                        title=str(payload.get("title") or "Başlık yok"),
                        abstract=str(
                            payload.get("abstract")
                            or payload.get("abstract_preview")
                            or ""
                        ),
                        vector=[float(value) for value in vector],
                    )
                )
            if offset is None:
                break
        return records

    def distance_method(self) -> str:
        """Canlı koleksiyonun yapılandırılmış uzaklık yöntemini döndürür."""

        info = self._client.get_collection(self._collection)
        vectors = info.config.params.vectors
        distance = getattr(vectors, "distance", None)
        return str(getattr(distance, "value", distance or "Bilinmiyor"))

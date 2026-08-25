import csv
from pathlib import Path
from typing import Any, Dict, Iterable, List, Protocol, Sequence

from ulakbim_analysis.domain.publication import Publication
from ulakbim_analysis.domain.vector_experiment import (
    ExperimentArticle,
    SimilarityResult,
    VectorPoint,
)


ABSTRACT_PREVIEW_LENGTH = 240
CSV_COLUMNS = (
    "query_uid",
    "query_title",
    "result_uid",
    "result_title",
    "cosine_score",
    "query_group",
    "result_group",
    "manual_label",
    "reviewer_note",
)


class Embedder(Protocol):
    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        ...

    def embed_query(self, text: str) -> List[float]:
        ...


class VectorStore(Protocol):
    def recreate_collection(self) -> None:
        ...

    def upsert(self, points: Sequence[VectorPoint]) -> None:
        ...

    def search(
        self,
        vector: Sequence[float],
        limit: int,
    ) -> List[SimilarityResult]:
        ...


def build_embedding_text(publication: Publication) -> str:
    title = publication.title or "Başlık yok"
    abstract = publication.abstract or "Abstract yok"
    return "Başlık: {0}\nAbstract: {1}".format(title, abstract)


def build_payload(article: ExperimentArticle) -> Dict[str, Any]:
    publication = article.publication
    abstract = publication.abstract or ""
    return {
        "uid": publication.uid,
        "title": publication.title,
        "journal": publication.journal,
        "publication_year": publication.publication_year,
        "subjects": publication.subjects,
        "experiment_group": article.group,
        "selection_reason": article.selection_reason,
        "abstract_preview": abstract[:ABSTRACT_PREVIEW_LENGTH],
    }


def create_vector_points(
    articles: Sequence[ExperimentArticle],
    embedder: Embedder,
) -> List[VectorPoint]:
    eligible = [
        article
        for article in articles
        if article.publication.abstract is not None
        and not article.publication.abstract_is_suspicious
    ]
    texts = [build_embedding_text(item.publication) for item in eligible]
    vectors = embedder.embed_documents(texts)
    if len(vectors) != len(eligible):
        raise ValueError("Embedding ve makale sayıları eşleşmiyor.")
    return [
        VectorPoint(
            uid=article.publication.uid,
            vector=vector,
            payload=build_payload(article),
        )
        for article, vector in zip(eligible, vectors)
    ]


def load_articles_to_store(
    articles: Sequence[ExperimentArticle],
    embedder: Embedder,
    store: VectorStore,
) -> int:
    points = create_vector_points(articles, embedder)
    store.recreate_collection()
    store.upsert(points)
    return len(points)


def search_similar(
    query_text: str,
    embedder: Embedder,
    store: VectorStore,
    query_uid: str = "",
    limit: int = 5,
) -> List[SimilarityResult]:
    vector = embedder.embed_query(query_text)
    candidates = store.search(vector, limit + (1 if query_uid else 0))
    filtered = [item for item in candidates if item.uid != query_uid]
    return sorted(filtered, key=lambda item: item.score, reverse=True)[:limit]


def write_comparison_csv(
    path: Path,
    rows: Iterable[Dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in CSV_COLUMNS})

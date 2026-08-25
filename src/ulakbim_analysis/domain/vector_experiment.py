from dataclasses import dataclass
from typing import Any, Dict, List

from ulakbim_analysis.domain.publication import Publication


@dataclass(frozen=True)
class ExperimentArticle:
    publication: Publication
    group: str
    selection_reason: str


@dataclass(frozen=True)
class VectorPoint:
    uid: str
    vector: List[float]
    payload: Dict[str, Any]


@dataclass(frozen=True)
class StoredArticleVector:
    """Qdrant'tan salt okunur olarak alınan makale vektörü."""

    article_id: str
    title: str
    abstract: str
    vector: List[float]


@dataclass(frozen=True)
class SimilarityResult:
    uid: str
    score: float
    title: str
    subjects: List[str]
    group: str
    abstract_preview: str

import csv
from pathlib import Path
from typing import Any, Dict, List, Sequence

from ulakbim_analysis.application.vector_experiment import (
    CSV_COLUMNS,
    build_embedding_text,
    build_payload,
    create_vector_points,
    search_similar,
    write_comparison_csv,
)
from ulakbim_analysis.application.vector_experiment_selection import (
    SELECTIONS,
    select_experiment_articles,
)
from ulakbim_analysis.domain.publication import Publication
from ulakbim_analysis.domain.vector_experiment import (
    ExperimentArticle,
    SimilarityResult,
)


class FakeEmbedder:
    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        return [[float(index), 1.0] for index, _ in enumerate(texts)]

    def embed_query(self, text: str) -> List[float]:
        return [1.0, 0.0]


class FakeStore:
    def search(
        self,
        vector: Sequence[float],
        limit: int,
    ) -> List[SimilarityResult]:
        return [
            SimilarityResult("LOW", 0.4, "Low", [], "g", "low"),
            SimilarityResult("SELF", 1.0, "Self", [], "g", "self"),
            SimilarityResult("HIGH", 0.9, "High", [], "g", "high"),
        ]


def make_article(publication: Publication) -> ExperimentArticle:
    return ExperimentArticle(publication, "test_group", "test reason")


def test_embedding_text_contains_title_and_abstract() -> None:
    publication = Publication(
        uid="UID",
        title="Makale başlığı",
        abstract="Makale özeti",
    )

    assert build_embedding_text(publication) == (
        "Başlık: Makale başlığı\nAbstract: Makale özeti"
    )


def test_ineligible_articles_are_not_embedded() -> None:
    articles = [
        make_article(Publication(uid="NO_ABSTRACT")),
        make_article(
            Publication(
                uid="SUSPICIOUS",
                abstract="şüpheli",
                abstract_length=8,
                abstract_is_suspicious=True,
            )
        ),
        make_article(Publication(uid="OK", title="T", abstract="A")),
    ]

    points = create_vector_points(articles, FakeEmbedder())

    assert [point.uid for point in points] == ["OK"]


def test_qdrant_payload_contains_required_fields() -> None:
    publication = Publication(
        uid="UID",
        title="Title",
        journal="Journal",
        publication_year=2024,
        subjects=["Physics"],
        abstract="A" * 300,
    )

    payload = build_payload(make_article(publication))

    assert payload["uid"] == "UID"
    assert payload["title"] == "Title"
    assert payload["journal"] == "Journal"
    assert payload["publication_year"] == 2024
    assert payload["subjects"] == ["Physics"]
    assert payload["experiment_group"] == "test_group"
    assert len(payload["abstract_preview"]) == 240


def test_search_excludes_self_and_orders_by_score() -> None:
    results = search_similar(
        "query",
        FakeEmbedder(),
        FakeStore(),
        query_uid="SELF",
        limit=2,
    )

    assert [result.uid for result in results] == ["HIGH", "LOW"]


def test_csv_report_has_expected_columns(tmp_path: Path) -> None:
    path = tmp_path / "report.csv"
    write_comparison_csv(path, [{"query_uid": "Q", "result_uid": "R"}])

    with path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    assert tuple(reader.fieldnames or []) == CSV_COLUMNS
    assert rows[0]["query_uid"] == "Q"
    assert rows[0]["manual_label"] == ""


def _raw_record(uid: str, abstract: Any) -> Dict[str, Any]:
    return {
        "UID": uid,
        "static_data": {
            "summary": {"titles": {"title": {"type": "item", "content": "T"}}},
            "fullrecord_metadata": {
                "abstracts": {"abstract": {"abstract_text": {"p": abstract}}}
            },
        },
    }


def test_selection_rejects_missing_and_suspicious_abstracts() -> None:
    selected_uids = list(SELECTIONS)[:3]
    records = [
        _raw_record(selected_uids[0], None),
        _raw_record(selected_uids[1], "a" * 10_001),
        _raw_record(selected_uids[2], "normal abstract"),
    ]

    selected = select_experiment_articles(records)

    assert [article.publication.uid for article in selected] == [selected_uids[2]]

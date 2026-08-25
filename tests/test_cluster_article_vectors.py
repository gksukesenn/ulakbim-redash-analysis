import csv
from pathlib import Path

from ulakbim_analysis.application.cluster_article_vectors import (
    CSV_COLUMNS,
    ClusterAssignment,
    cluster_vectors,
    write_assignments_csv,
    write_summary,
)
from ulakbim_analysis.domain.vector_experiment import StoredArticleVector


def _articles():
    return [
        StoredArticleVector("A", "Alpha", "", [0.0, 0.0, 0.0]),
        StoredArticleVector("B", "Beta", "", [0.1, 0.0, 0.0]),
        StoredArticleVector("C", "Gamma", "", [5.0, 5.0, 5.0]),
        StoredArticleVector("D", "Delta", "", [5.1, 5.0, 5.0]),
        StoredArticleVector("E", "Epsilon", "", [10.0, 0.0, 0.0]),
        StoredArticleVector("F", "Zeta", "", [10.1, 0.0, 0.0]),
    ]


def test_cluster_vectors_returns_two_dimensional_assignments() -> None:
    assignments, explained_variance, inertia = cluster_vectors(_articles())

    assert len(assignments) == 6
    assert len({item.cluster for item in assignments}) == 3
    assert all(isinstance(item.pca_x, float) for item in assignments)
    assert len(explained_variance) == 2
    assert inertia >= 0


def test_assignment_csv_has_required_columns(tmp_path: Path) -> None:
    path = tmp_path / "assignments.csv"
    assignment = ClusterAssignment("A", "Alpha", 1, 0.25, -0.5)

    write_assignments_csv(path, [assignment])

    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        rows = list(reader)
    assert tuple(reader.fieldnames or []) == CSV_COLUMNS
    assert rows[0]["article_id"] == "A"
    assert rows[0]["cluster"] == "1"


def test_summary_contains_method_and_cluster_titles(tmp_path: Path) -> None:
    path = tmp_path / "summary.md"
    assignments = [ClusterAssignment("A", "Alpha", 0, 0.0, 0.0)]

    write_summary(path, assignments, "test-model", "Cosine", [0.6, 0.2], 1.5)

    report = path.read_text(encoding="utf-8")
    assert "Toplam makale sayısı: **1**" in report
    assert "test-model" in report
    assert "Cosine" in report
    assert "Alpha" in report

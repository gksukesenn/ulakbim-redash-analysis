import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

from ulakbim_analysis.domain.vector_experiment import StoredArticleVector
from ulakbim_analysis.infrastructure.qdrant_vector_store import QdrantVectorStore
from ulakbim_analysis.infrastructure.vector_settings import VectorExperimentSettings


PLOT_PATH = Path("reports/article_clusters_pca.png")
CSV_PATH = Path("reports/article_cluster_assignments.csv")
REPORT_PATH = Path("reports/article_cluster_summary.md")
CSV_COLUMNS = ("article_id", "title", "cluster", "pca_x", "pca_y")


@dataclass(frozen=True)
class ClusterAssignment:
    article_id: str
    title: str
    cluster: int
    pca_x: float
    pca_y: float


def cluster_vectors(
    articles: Sequence[StoredArticleVector],
    cluster_count: int = 3,
) -> Tuple[List[ClusterAssignment], List[float], float]:
    """Vektörleri PCA'ya indirger ve deterministik KMeans uygular."""

    try:
        from sklearn.cluster import KMeans
        from sklearn.decomposition import PCA
    except ImportError as error:
        raise RuntimeError(
            "Kümeleme bağımlılıkları eksik; `pip install -e '.[cluster]'` "
            "komutunu çalıştırın."
        ) from error

    if len(articles) < cluster_count:
        raise ValueError("Makale sayısı küme sayısından küçük olamaz.")
    dimensions = {len(article.vector) for article in articles}
    if len(dimensions) != 1 or not dimensions or 0 in dimensions:
        raise ValueError("Makale vektör boyutları boş veya birbiriyle uyumsuz.")

    vectors = [article.vector for article in articles]
    pca = PCA(n_components=2)
    coordinates = pca.fit_transform(vectors)
    model = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
    labels = model.fit_predict(vectors)
    assignments = [
        ClusterAssignment(
            article_id=article.article_id,
            title=article.title,
            cluster=int(label),
            pca_x=float(point[0]),
            pca_y=float(point[1]),
        )
        for article, label, point in zip(articles, labels, coordinates)
    ]
    return (
        assignments,
        [float(value) for value in pca.explained_variance_ratio_],
        float(model.inertia_),
    )


def write_assignments_csv(
    path: Path,
    assignments: Sequence[ClusterAssignment],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for item in assignments:
            writer.writerow(
                {
                    "article_id": item.article_id,
                    "title": item.title,
                    "cluster": item.cluster,
                    "pca_x": "{0:.8f}".format(item.pca_x),
                    "pca_y": "{0:.8f}".format(item.pca_y),
                }
            )


def _short_title(title: str, length: int = 34) -> str:
    return title if len(title) <= length else title[: length - 1].rstrip() + "…"


def write_pca_plot(
    path: Path,
    assignments: Sequence[ClusterAssignment],
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise RuntimeError(
            "Grafik bağımlılığı eksik; `pip install -e '.[cluster]'` "
            "komutunu çalıştırın."
        ) from error

    path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(15, 10))
    colors = ("#0072B2", "#D55E00", "#009E73")
    for cluster in sorted({item.cluster for item in assignments}):
        members = [item for item in assignments if item.cluster == cluster]
        axis.scatter(
            [item.pca_x for item in members],
            [item.pca_y for item in members],
            s=85,
            alpha=0.85,
            color=colors[cluster % len(colors)],
            label="Küme {0} (n={1})".format(cluster, len(members)),
        )
        for item in members:
            axis.annotate(
                "C{0} · {1}".format(cluster, _short_title(item.title)),
                (item.pca_x, item.pca_y),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=7,
            )
    axis.set_title("Makale embedding vektörleri: PCA ve KMeans (k=3)")
    axis.set_xlabel("PCA bileşeni 1")
    axis.set_ylabel("PCA bileşeni 2")
    axis.grid(alpha=0.2)
    axis.legend()
    figure.tight_layout()
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def write_summary(
    path: Path,
    assignments: Sequence[ClusterAssignment],
    embedding_model: str,
    distance_method: str,
    explained_variance_ratio: Sequence[float],
    kmeans_inertia: float,
) -> None:
    lines = [
        "# Makale vektörleri keşifsel kümeleme özeti",
        "",
        "- Toplam makale sayısı: **{0}**".format(len(assignments)),
        "- Kullanılan embedding modeli: `{0}`".format(embedding_model),
        "- Qdrant uzaklık/benzerlik yöntemi: **{0}** (cosine benzerliği, "
        "vektörlerin yönsel yakınlığını karşılaştırır).".format(distance_method),
        "- Kümeleme: KMeans, `k=3`, `random_state=42`, `n_init=10`.",
        "- PCA açıklanan varyans: PC1 **{0:.2%}**, PC2 **{1:.2%}**, toplam "
        "**{2:.2%}**.".format(
            explained_variance_ratio[0],
            explained_variance_ratio[1],
            sum(explained_variance_ratio),
        ),
        "- KMeans inertia (küme içi kareler toplamı): **{0:.6f}**.".format(
            kmeans_inertia
        ),
        "",
        "## Yöntem",
        "",
        "PCA, 384 boyutlu embedding vektörlerindeki varyansı mümkün olduğunca "
        "koruyarak iki görsel eksene indirger. KMeans ise vektör uzayında "
        "Öklid uzaklığına göre noktaları üç küme merkezine atar. PCA yalnızca "
        "görselleştirme için kullanılmış; KMeans özgün embedding vektörleri "
        "üzerinde çalıştırılmıştır. Sonuçlar keşifseldir ve ground truth etiketi "
        "olarak yorumlanmamalıdır.",
        "",
        "## Kümeler",
        "",
    ]
    for cluster in sorted({item.cluster for item in assignments}):
        members = sorted(
            (item for item in assignments if item.cluster == cluster),
            key=lambda item: item.title.casefold(),
        )
        lines.extend(
            [
                "### Küme {0} — {1} makale".format(cluster, len(members)),
                "",
            ]
        )
        lines.extend(
            "- `{0}` — {1}".format(item.article_id, item.title)
            for item in members
        )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    settings = VectorExperimentSettings.from_env()
    store = QdrantVectorStore(
        url=settings.qdrant_url,
        collection=settings.collection,
        dimension=settings.vector_dimension,
    )
    store.check_connection()
    articles = store.read_all_articles()
    assignments, explained_variance_ratio, kmeans_inertia = cluster_vectors(
        articles
    )
    write_assignments_csv(CSV_PATH, assignments)
    write_pca_plot(PLOT_PATH, assignments)
    write_summary(
        REPORT_PATH,
        assignments,
        settings.embedding_model,
        store.distance_method(),
        explained_variance_ratio,
        kmeans_inertia,
    )
    print("Analiz edilen makale: {0}".format(len(assignments)))
    print("PCA grafiği: {0}".format(PLOT_PATH))
    print("Küme atamaları: {0}".format(CSV_PATH))
    print("Özet rapor: {0}".format(REPORT_PATH))


if __name__ == "__main__":
    main()

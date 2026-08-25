from pathlib import Path
from typing import Any, Dict, List, Sequence

from ulakbim_analysis.application.vector_experiment import (
    build_embedding_text,
    search_similar,
    write_comparison_csv,
)
from ulakbim_analysis.application.vector_experiment_runtime import (
    create_vector_services,
)
from ulakbim_analysis.application.vector_experiment_selection import (
    load_experiment_articles,
)
from ulakbim_analysis.domain.vector_experiment import (
    ExperimentArticle,
    SimilarityResult,
)
from ulakbim_analysis.infrastructure.vector_settings import (
    DEFAULT_EMBEDDING_MODEL,
)


REPORT_PATH = Path("reports/vector_similarity_experiment.md")
CSV_PATH = Path("reports/vector_similarity_results.csv")
EXAMPLE_QUERY_UIDS = (
    "WOS:001140573400001",
    "WOS:001163332000001",
    "WOS:001157724100001",
)


def _comparison_rows(
    articles: Sequence[ExperimentArticle],
    all_results: Dict[str, List[SimilarityResult]],
) -> List[Dict[str, Any]]:
    by_uid = {article.publication.uid: article for article in articles}
    rows = []
    for article in articles:
        publication = article.publication
        for result in all_results[publication.uid]:
            rows.append(
                {
                    "query_uid": publication.uid,
                    "query_title": publication.title or "",
                    "result_uid": result.uid,
                    "result_title": result.title,
                    "cosine_score": "{0:.6f}".format(result.score),
                    "query_group": article.group,
                    "result_group": by_uid[result.uid].group,
                    "manual_label": "",
                    "reviewer_note": "",
                }
            )
    return rows


def _result_lines(results: Sequence[SimilarityResult]) -> List[str]:
    lines = []
    for index, result in enumerate(results, start=1):
        lines.append(
            "{0}. `{1}` — {2:.6f} — {3} — `{4}`".format(
                index,
                result.uid,
                result.score,
                result.title,
                result.group,
            )
        )
    return lines


def write_markdown_report(
    path: Path,
    articles: Sequence[ExperimentArticle],
    all_results: Dict[str, List[SimilarityResult]],
) -> None:
    rows = _comparison_rows(articles, all_results)
    highest = max(rows, key=lambda row: float(row["cosine_score"]))
    lowest = min(rows, key=lambda row: float(row["cosine_score"]))
    cross_group = [
        row for row in rows if row["query_group"] != row["result_group"]
    ]
    boundary = max(cross_group, key=lambda row: float(row["cosine_score"]))
    article_by_uid = {
        article.publication.uid: article for article in articles
    }
    examples = [article_by_uid[uid] for uid in EXAMPLE_QUERY_UIDS]

    lines = [
        "# Vektör benzerliği öğrenme deneyi",
        "",
        "## Amaç",
        "",
        "Bu deney 24 kontrollü makaleyi embedding vektörlerine dönüştürür, "
        "Qdrant'ta saklar ve cosine similarity sıralamasını insan gözüyle "
        "incelemeye açar. Skor bir doğruluk yüzdesi değildir.",
        "",
        "## Model seçimi",
        "",
        "Model: `{0}`. Model cümle ve paragrafları 384 boyutlu yoğun "
        "vektörlere dönüştürür; 50 dili destekler ve Apache-2.0 "
        "lisanslıdır. FastEmbed'in ONNX çalıştırıcısı CPU üzerinde yerel "
        "çalışır; API anahtarı veya ücretli servis kullanmaz. Küçük deney "
        "için yaklaşık 220 MB'lık model, daha büyük çok dilli modellere göre "
        "daha kolay tekrarlanabilir.".format(DEFAULT_EMBEDDING_MODEL),
        "",
        "Embedding girdisi açıkça `Başlık: ...\\nAbstract: ...` şablonudur. "
        "Abstract'sız ve şüpheli abstract'lı kayıtlar yüklenmez.",
        "",
        "## Qdrant kavramları",
        "",
        "- **Collection:** Aynı vektör şemasını kullanan point kümesi; bu "
        "deneyin ayrı tablosu gibi düşünülebilir.",
        "- **Point:** Bir makaleyi temsil eden kayıt; kimlik, vector ve "
        "payload içerir.",
        "- **Vector:** Metnin anlamını sayılarla temsil eden 384 elemanlı "
        "embedding.",
        "- **Payload:** UID, başlık, dergi, yıl, subjects, deney grubu ve kısa "
        "abstract önizlemesi gibi okunabilir metadata.",
        "- **Vector dimension:** Her vector içindeki sayı adedi; burada 384.",
        "- **Distance metric:** Qdrant sıralamada cosine benzerliğini kullanır; "
        "vektörlerin yönlerinin ne kadar benzer olduğunu karşılaştırır.",
        "",
        "## Seçilen makale grupları",
        "",
    ]
    current_group = ""
    for article in sorted(articles, key=lambda item: item.group):
        if article.group != current_group:
            if current_group:
                lines.append("")
            current_group = article.group
            lines.extend(["### `{0}`".format(current_group), ""])
        lines.append(
            "- `{0}` — {1} — seçim nedeni: {2}".format(
                article.publication.uid,
                article.publication.title,
                article.selection_reason,
            )
        )

    lines.extend(["", "## Örnek arama sonuçları", ""])
    for article in examples:
        lines.extend(
            [
                "### `{0}` — {1}".format(
                    article.publication.uid,
                    article.publication.title,
                ),
                "",
            ]
        )
        lines.extend(_result_lines(all_results[article.publication.uid]))
        lines.append("")

    lines.extend(
        [
            "## Gözlem adayları",
            "",
            "- En yüksek karşılaştırma: `{0}` → `{1}`, skor {2}.".format(
                highest["query_uid"], highest["result_uid"],
                highest["cosine_score"],
            ),
            "- Raporlanan en düşük ilk-5 karşılaştırması: `{0}` → `{1}`, "
            "skor {2}.".format(
                lowest["query_uid"], lowest["result_uid"],
                lowest["cosine_score"],
            ),
            "- Gruplar arası en yüksek sınır adayı: `{0}` → `{1}`, skor "
            "{2}. Bu çift özellikle `manual_label` ve `reviewer_note` "
            "alanlarında incelenmelidir.".format(
                boundary["query_uid"], boundary["result_uid"],
                boundary["cosine_score"],
            ),
            "",
            "## Neden evrensel bir eşik yok?",
            "",
            "Cosine skorlarının ölçeği modele, metin şablonuna, dil ve konu "
            "dağılımına bağlıdır. Aynı skor bir veri setinde güçlü, başka bir "
            "veri setinde zayıf ilişki anlamına gelebilir. Bu nedenle otomatik "
            "etiket atanmadı; CSV'deki `manual_label` alanı insan incelemesine "
            "bırakıldı.",
            "",
            "## 100 ve 1.000 kayda geçmeden önce",
            "",
            "- Aynı, yakın ve farklı grup çiftlerini elle etiketleyip hata "
            "örüntülerini karşılaştırın.",
            "- Başlık ve abstract katkısını ayrı deneylerle ölçün.",
            "- 512 token model sınırında uzun abstract kesilmesinin etkisini "
            "inceleyin.",
            "- Türkçe ve düşük temsil edilen diller için ayrıca örnek seçin.",
            "- Model ve veri seçimini sabitleyip tekrarlanabilirliği doğrulayın.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_reports() -> None:
    articles = load_experiment_articles()
    embedder, store = create_vector_services()
    all_results = {}
    for article in articles:
        publication = article.publication
        all_results[publication.uid] = search_similar(
            build_embedding_text(publication),
            embedder,
            store,
            query_uid=publication.uid,
            limit=5,
        )
    rows = _comparison_rows(articles, all_results)
    write_comparison_csv(CSV_PATH, rows)
    write_markdown_report(REPORT_PATH, articles, all_results)
    print("Markdown raporu: {0}".format(REPORT_PATH))
    print("CSV raporu: {0} ({1} karşılaştırma)".format(CSV_PATH, len(rows)))


if __name__ == "__main__":
    generate_reports()

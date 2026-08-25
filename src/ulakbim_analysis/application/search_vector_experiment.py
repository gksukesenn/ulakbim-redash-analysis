import argparse
from typing import List, Optional, Sequence, Tuple

from ulakbim_analysis.application.vector_experiment import (
    build_embedding_text,
    search_similar,
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


def resolve_query(
    articles: Sequence[ExperimentArticle],
    uid: Optional[str],
    text: Optional[str],
) -> Tuple[str, str]:
    if text:
        return text, ""
    for article in articles:
        if article.publication.uid == uid:
            return build_embedding_text(article.publication), str(uid)
    raise ValueError("UID seçili deney makaleleri arasında bulunamadı: {0}".format(uid))


def print_results(results: List[SimilarityResult]) -> None:
    print("Cosine similarity sonuçları (skor doğruluk yüzdesi değildir):")
    for rank, result in enumerate(results, start=1):
        print("\n{0}. skor={1:.6f}".format(rank, result.score))
        print("   UID: {0}".format(result.uid))
        print("   Başlık: {0}".format(result.title))
        print("   Subjects: {0}".format(", ".join(result.subjects)))
        print("   Deney grubu: {0}".format(result.group))
        print("   Abstract önizleme: {0}".format(result.abstract_preview))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Qdrant benzer makale araması")
    query = parser.add_mutually_exclusive_group(required=True)
    query.add_argument("--uid")
    query.add_argument("--text")
    parser.add_argument("--limit", type=int, default=5)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    if not 1 <= args.limit <= 5:
        raise ValueError("limit 1 ile 5 arasında olmalıdır.")
    articles = load_experiment_articles()
    query_text, query_uid = resolve_query(articles, args.uid, args.text)
    embedder, store = create_vector_services()
    results = search_similar(
        query_text,
        embedder,
        store,
        query_uid=query_uid,
        limit=args.limit,
    )
    print_results(results)


if __name__ == "__main__":
    main()

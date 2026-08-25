from collections import Counter

from ulakbim_analysis.application.vector_experiment_selection import (
    SELECTIONS,
    load_experiment_articles,
)


def main() -> None:
    articles = load_experiment_articles()
    counts = Counter(article.group for article in articles)
    print("Seçilen deney makaleleri: {0}/{1}".format(
        len(articles), len(SELECTIONS)
    ))
    for group, count in sorted(counts.items()):
        print("\n{0} ({1} makale)".format(group, count))
        for article in articles:
            if article.group != group:
                continue
            publication = article.publication
            print(
                "  - {0} | {1} | {2}".format(
                    publication.uid,
                    publication.title or "Başlık yok",
                    article.selection_reason,
                )
            )


if __name__ == "__main__":
    main()

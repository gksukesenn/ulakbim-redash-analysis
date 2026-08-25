from ulakbim_analysis.application.vector_experiment import (
    load_articles_to_store,
)
from ulakbim_analysis.application.vector_experiment_runtime import (
    create_vector_services,
)
from ulakbim_analysis.application.vector_experiment_selection import (
    load_experiment_articles,
)


def main() -> None:
    articles = load_experiment_articles()
    embedder, store = create_vector_services()
    loaded = load_articles_to_store(articles, embedder, store)
    print("Qdrant'a yüklenen deney makalesi: {0}".format(loaded))


if __name__ == "__main__":
    main()

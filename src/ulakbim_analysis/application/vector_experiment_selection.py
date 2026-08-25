from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from ulakbim_analysis.domain.vector_experiment import ExperimentArticle
from ulakbim_analysis.infrastructure.json_reader import iter_publications
from ulakbim_analysis.infrastructure.publication_mapper import map_publication


DATA_FILE = Path("data/raw/ulakbim_ubyt_wos_records.json")

GROUP_SAME_TOPIC = "same_topic_perovskite_solar_cells"
GROUP_RELATED = "related_energy_technologies"
GROUP_DIFFERENT = "different_mental_health"

SELECTIONS: Dict[str, Tuple[str, str]] = {
    "WOS:001140573400001": (GROUP_SAME_TOPIC, "Perovskit hücre kararlılığı"),
    "WOS:001167231700001": (GROUP_SAME_TOPIC, "Perovskit malzeme katkılama"),
    "WOS:001178378200001": (GROUP_SAME_TOPIC, "Perovskit taşıma malzemesi"),
    "WOS:001191208900001": (GROUP_SAME_TOPIC, "Perovskit ara katmanı"),
    "WOS:001158980200001": (GROUP_SAME_TOPIC, "Perovskit pasivasyonu"),
    "WOS:001173733800001": (GROUP_SAME_TOPIC, "Perovskit temas kararlılığı"),
    "WOS:001143809700001": (GROUP_SAME_TOPIC, "Kalay perovskit fotovoltaik"),
    "WOS:001131514500001": (GROUP_SAME_TOPIC, "Yönelimli perovskit"),
    "WOS:001168109200001": (GROUP_RELATED, "Sodyum iyon batarya"),
    "WOS:001144493500001": (GROUP_RELATED, "Lityum iyon katot"),
    "WOS:001165771600001": (GROUP_RELATED, "Batarya termal yönetimi"),
    "WOS:001149960200001": (GROUP_RELATED, "Batarya yönetim sistemleri"),
    "WOS:001140575800001": (GROUP_RELATED, "Süperkapasitör elektroliti"),
    "WOS:001143201300001": (GROUP_RELATED, "Süperkapasitör elektrodu"),
    "WOS:001163332000001": (GROUP_RELATED, "Boya duyarlı güneş hücresi"),
    "WOS:001168628400001": (GROUP_RELATED, "Fotovoltaik güç tahmini"),
    "WOS:001157724100001": (GROUP_DIFFERENT, "Deprem sonrası depresyon"),
    "WOS:001154920600001": (GROUP_DIFFERENT, "Doğum sonrası depresyon"),
    "WOS:001157189800001": (GROUP_DIFFERENT, "Perinatal depresyon terapisi"),
    "WOS:001182798400001": (GROUP_DIFFERENT, "Giyilebilirlerle ruh sağlığı"),
    "WOS:001148762500002": (GROUP_DIFFERENT, "Bağlanma ve anksiyete"),
    "WOS:001142171500001": (GROUP_DIFFERENT, "Anksiyete biyobelirteçleri"),
    "WOS:001129852800002": (GROUP_DIFFERENT, "Yaşlılarda anksiyete/depresyon"),
    "WOS:001163480800004": (GROUP_DIFFERENT, "Kanserde stres ve depresyon"),
}


def select_experiment_articles(
    raw_publications: Iterable[dict],
) -> List[ExperimentArticle]:
    selected = []
    remaining_uids = set(SELECTIONS)

    for raw_publication in raw_publications:
        uid = raw_publication.get("UID")
        if uid not in remaining_uids:
            continue

        publication = map_publication(raw_publication)
        remaining_uids.remove(uid)
        if publication.abstract is None or publication.abstract_is_suspicious:
            continue

        group, reason = SELECTIONS[uid]
        selected.append(
            ExperimentArticle(
                publication=publication,
                group=group,
                selection_reason=reason,
            )
        )
        if not remaining_uids:
            break

    return sorted(selected, key=lambda article: article.publication.uid)


def load_experiment_articles(
    file_path: Path = DATA_FILE,
) -> List[ExperimentArticle]:
    return select_experiment_articles(iter_publications(file_path))

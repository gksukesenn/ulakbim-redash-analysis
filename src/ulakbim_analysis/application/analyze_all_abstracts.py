from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median
from time import monotonic
from typing import Any, Callable, Dict, Iterable, List, Optional

from ulakbim_analysis.domain.publication import (
    ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD,
    Publication,
)
from ulakbim_analysis.infrastructure.json_reader import iter_publications
from ulakbim_analysis.infrastructure.publication_mapper import (
    as_dict,
    as_list,
    map_publication,
)


DATA_FILE = Path("data/raw/ulakbim_ubyt_wos_records.json")
PROGRESS_INTERVAL = 10_000
MAX_DISPLAYED_ERRORS = 5

DISTRIBUTION_LABELS = (
    "0",
    "1–1.000",
    "1.001–2.500",
    "2.501–5.000",
    "5.001–10.000",
    "10.000 üzeri",
)


@dataclass(frozen=True)
class AbstractAnalysisError:
    uid: str
    error_type: str
    message: str


@dataclass(frozen=True)
class SuspiciousAbstract:
    uid: str
    length: int
    paragraph_count: Optional[int]


@dataclass
class AbstractAnalysisResult:
    inspected: int = 0
    successful: int = 0
    mapping_errors: int = 0
    with_abstract: int = 0
    without_abstract: int = 0
    suspicious_count: int = 0
    shortest_normal_length: Optional[int] = None
    longest_normal_length: Optional[int] = None
    average_normal_length: Optional[float] = None
    median_normal_length: Optional[float] = None
    duration_seconds: float = 0.0
    distribution: Counter = field(default_factory=Counter)
    suspicious_abstracts: List[SuspiciousAbstract] = field(
        default_factory=list
    )
    errors: List[AbstractAnalysisError] = field(default_factory=list)


def abstract_length_bucket(length: int) -> str:
    if length == 0:
        return DISTRIBUTION_LABELS[0]
    if length <= 1_000:
        return DISTRIBUTION_LABELS[1]
    if length <= 2_500:
        return DISTRIBUTION_LABELS[2]
    if length <= 5_000:
        return DISTRIBUTION_LABELS[3]
    if length <= ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD:
        return DISTRIBUTION_LABELS[4]
    return DISTRIBUTION_LABELS[5]


def count_abstract_paragraphs(raw_publication: Dict[str, Any]) -> Optional[int]:
    static_data = as_dict(raw_publication.get("static_data"))
    metadata = as_dict(static_data.get("fullrecord_metadata"))
    abstracts = as_dict(metadata.get("abstracts"))
    count = 0

    for abstract_item in as_list(abstracts.get("abstract")):
        abstract = as_dict(abstract_item)
        abstract_text = as_dict(abstract.get("abstract_text"))
        paragraphs = abstract_text.get("p")
        if isinstance(paragraphs, str):
            count += 1
        elif isinstance(paragraphs, list):
            count += len(paragraphs)

    return count or None


def analyze_abstract_records(
    raw_publications: Iterable[Dict[str, Any]],
    mapper: Callable[[Dict[str, Any]], Publication] = map_publication,
    progress_interval: int = PROGRESS_INTERVAL,
    max_displayed_errors: int = MAX_DISPLAYED_ERRORS,
) -> AbstractAnalysisResult:
    """Kayıt akışını tarar; medyan için yalnız normal uzunlukları tutar."""

    if progress_interval <= 0:
        raise ValueError("progress_interval pozitif olmalıdır.")
    if max_displayed_errors < 0:
        raise ValueError("max_displayed_errors negatif olamaz.")

    result = AbstractAnalysisResult()
    normal_lengths: List[int] = []
    normal_length_sum = 0
    started_at = monotonic()

    for raw_publication in raw_publications:
        result.inspected += 1
        if result.inspected % progress_interval == 0:
            print("İlerleme: {0:,} kayıt tarandı.".format(result.inspected))

        try:
            publication = mapper(raw_publication)
        except Exception as error:
            result.mapping_errors += 1
            if len(result.errors) < max_displayed_errors:
                result.errors.append(
                    AbstractAnalysisError(
                        uid=str(raw_publication.get("UID", "Bilinmiyor")),
                        error_type=type(error).__name__,
                        message=str(error),
                    )
                )
            continue

        result.successful += 1
        length = publication.abstract_length
        result.distribution[abstract_length_bucket(length)] += 1

        if publication.abstract is None:
            result.without_abstract += 1
            continue

        result.with_abstract += 1
        if publication.abstract_is_suspicious:
            result.suspicious_count += 1
            result.suspicious_abstracts.append(
                SuspiciousAbstract(
                    uid=publication.uid,
                    length=length,
                    paragraph_count=count_abstract_paragraphs(
                        raw_publication
                    ),
                )
            )
            continue

        normal_lengths.append(length)
        normal_length_sum += length

    if normal_lengths:
        result.shortest_normal_length = min(normal_lengths)
        result.longest_normal_length = max(normal_lengths)
        result.average_normal_length = (
            normal_length_sum / len(normal_lengths)
        )
        result.median_normal_length = float(median(normal_lengths))

    result.duration_seconds = monotonic() - started_at
    return result


def print_analysis_result(result: AbstractAnalysisResult) -> None:
    print("\nTüm veri seti abstract analizi")
    print("------------------------------")
    print("İncelenen toplam kayıt: {0}".format(result.inspected))
    print("Başarılı dönüşüm: {0}".format(result.successful))
    print("Dönüşüm hatası: {0}".format(result.mapping_errors))
    print("Abstract bulunan kayıt: {0}".format(result.with_abstract))
    print("Abstract bulunmayan kayıt: {0}".format(result.without_abstract))
    print("Şüpheli abstract: {0}".format(result.suspicious_count))
    print("En kısa normal abstract: {0}".format(result.shortest_normal_length))
    print("En uzun normal abstract: {0}".format(result.longest_normal_length))
    average = result.average_normal_length
    median_length = result.median_normal_length
    print(
        "Normal abstract ortalaması: {0}".format(
            "Yok" if average is None else "{0:.2f}".format(average)
        )
    )
    print(
        "Normal abstract medyanı: {0}".format(
            "Yok" if median_length is None else "{0:g}".format(median_length)
        )
    )

    print("\nAbstract uzunluk dağılımı:")
    for label in DISTRIBUTION_LABELS:
        print("  - {0}: {1}".format(label, result.distribution[label]))

    print("\nŞüpheli abstractlar:")
    if not result.suspicious_abstracts:
        print("  - Yok")
    for item in result.suspicious_abstracts:
        paragraph_count = (
            "Bilinmiyor"
            if item.paragraph_count is None
            else str(item.paragraph_count)
        )
        print(
            "  - UID: {0}, uzunluk: {1}, paragraf sayısı: {2}".format(
                item.uid,
                item.length,
                paragraph_count,
            )
        )

    if result.errors:
        print("\nİlk dönüşüm hataları:")
        for error in result.errors:
            print(
                "  - UID: {0} — {1}: {2}".format(
                    error.uid,
                    error.error_type,
                    error.message,
                )
            )
    print("\nToplam süre: {0:.2f} saniye".format(result.duration_seconds))


def analyze_all_abstracts(file_path: Path = DATA_FILE) -> AbstractAnalysisResult:
    result = analyze_abstract_records(iter_publications(file_path))
    print_analysis_result(result)
    return result


if __name__ == "__main__":
    analyze_all_abstracts()

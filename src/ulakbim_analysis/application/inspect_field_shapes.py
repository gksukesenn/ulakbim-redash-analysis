from collections import Counter
from pathlib import Path
from typing import Any, Dict, Tuple

from ulakbim_analysis.infrastructure.json_reader import iter_publications


MISSING = object()

FIELD_PATHS = {
    "Yayıncı": (
        "static_data",
        "summary",
        "publishers",
        "publisher",
    ),
    "Başlıklar": (
        "static_data",
        "summary",
        "titles",
        "title",
    ),
    "Kurum ve adres": (
        "static_data",
        "fullrecord_metadata",
        "addresses",
        "address_name",
    ),
    "Konular": (
        "static_data",
        "fullrecord_metadata",
        "category_info",
        "subjects",
        "subject",
    ),
    "Diller": (
        "static_data",
        "fullrecord_metadata",
        "languages",
        "language",
    ),
    "Doküman türleri": (
        "static_data",
        "summary",
        "doctypes",
        "doctype",
    ),
    "Gold Open Access": (
        "static_data",
        "summary",
        "pub_info",
        "journal_oas_gold",
    ),
    "Yayın yılı": (
        "static_data",
        "summary",
        "pub_info",
        "pubyear",
    ),
}


def get_nested_value(
    data: Dict[str, Any],
    path: Tuple[str, ...],
) -> Any:
    """
    İç içe geçmiş bir sözlükte belirtilen yolu takip eder.

    Yol bulunamazsa özel MISSING değerini döndürür.
    """

    current_value: Any = data

    for key in path:
        if not isinstance(current_value, dict):
            return MISSING

        if key not in current_value:
            return MISSING

        current_value = current_value[key]

    return current_value


def get_value_type(value: Any) -> str:
    """
    Bir alanın veri tipini okunabilir biçimde döndürür.
    """

    if value is MISSING:
        return "eksik"

    if value is None:
        return "null"

    return type(value).__name__


def inspect_field_shapes(
    file_path: Path,
    limit: int = 1000,
) -> None:
    """
    İlk belirli sayıdaki yayında önemli alanların
    hangi veri tiplerinde geldiğini inceler.
    """

    type_counts = {
        field_name: Counter()
        for field_name in FIELD_PATHS
    }

    open_access_values = Counter()
    inspected_count = 0

    for publication in iter_publications(file_path):
        inspected_count += 1

        for field_name, field_path in FIELD_PATHS.items():
            value = get_nested_value(
                publication,
                field_path,
            )

            value_type = get_value_type(value)
            type_counts[field_name][value_type] += 1

            if (
                field_name == "Gold Open Access"
                and value is not MISSING
                and value is not None
            ):
                open_access_values[str(value)] += 1

        if inspected_count >= limit:
            break

    print(f"İncelenen yayın sayısı: {inspected_count}")

    for field_name, counts in type_counts.items():
        print(f"\n{field_name} alanı:")

        for value_type, count in counts.most_common():
            print(f"  - {value_type}: {count}")

    print("\nGold Open Access değerleri:")

    if not open_access_values:
        print("  Değer bulunamadı.")
        return

    for value, count in open_access_values.most_common():
        print(f"  - {value!r}: {count}")

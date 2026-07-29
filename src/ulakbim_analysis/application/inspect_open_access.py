from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple

from ulakbim_analysis.infrastructure.json_reader import iter_publications

def is_open_access_key(key: str) -> bool:
    """
    Bir alan adının gerçek Open Access bilgisiyle
    ilişkili görünüp görünmediğini kontrol eder.

    early_access gibi farklı anlamdaki alanları eşleştirmez.
    """
    normalized_key = key.lower()

    exact_keys = {
        "journal_oas_gold",
        "open_access",
        "openaccess",
        "is_open_access",
        "oa_status",
    }

    return (
        normalized_key in exact_keys
        or normalized_key.startswith("oa_")
        or normalized_key.endswith("_oa")
    )

def summarize_value(value: Any) -> str:
    """
    Büyük nesneleri tamamen yazdırmadan kısa bir özet oluşturur.
    """
    if isinstance(value, dict):
        return f"dict, anahtarlar={list(value.keys())}"

    if isinstance(value, list):
        return f"list, eleman sayısı={len(value)}"

    return repr(value)


def iter_matching_fields(
    value: Any,
    path: str = "",
) -> Iterator[Tuple[str, Any]]:
    """
    İç içe JSON yapısında Open Access ile ilişkili
    alanları özyinelemeli olarak arar.
    """
    if isinstance(value, dict):
        for key, child_value in value.items():
            current_path = (
                f"{path}.{key}"
                if path
                else key
            )

            if is_open_access_key(key):
                yield current_path, child_value

            yield from iter_matching_fields(
                child_value,
                current_path,
            )

    elif isinstance(value, list):
        # Aynı yapıdaki yüzlerce elemanı tekrar tekrar
        # incelememek için ilk üç örneğe bakıyoruz.
        for child_value in value[:3]:
            yield from iter_matching_fields(
                child_value,
                f"{path}[]",
            )


def inspect_open_access_fields(
    file_path: Path,
    limit: int = 100,
) -> None:
    """
    İlk belirli sayıdaki yayını inceleyerek Open Access
    ile ilişkili alan yollarını ve örnek değerleri gösterir.
    """
    results: Dict[str, List[str]] = {}
    inspected_count = 0

    for publication in iter_publications(file_path):
        inspected_count += 1

        for field_path, value in iter_matching_fields(publication):
            value_summary = summarize_value(value)

            samples = results.setdefault(field_path, [])

            if (
                value_summary not in samples
                and len(samples) < 5
            ):
                samples.append(value_summary)

        if inspected_count >= limit:
            break

    print(f"İncelenen yayın sayısı: {inspected_count}")

    if not results:
        print("Open Access ile ilişkili alan bulunamadı.")
        return

    print("\nBulunan alanlar:")

    for field_path in sorted(results):
        print(f"\n- {field_path}")

        for sample in results[field_path]:
            print(f"    Örnek: {sample}")

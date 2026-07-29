from pathlib import Path
from typing import Any, Dict

from ulakbim_analysis.infrastructure.json_reader import iter_publications


def print_dict_keys(title: str, data: Any) -> None:
    """
    Verilen değer bir sözlükse anahtarlarını ekrana yazdırır.
    """

    print(f"\n{title}")

    if not isinstance(data, dict):
        print("  Beklenen nesne yapısı bulunamadı.")
        return

    for key in data.keys():
        print(f"  - {key}")


def inspect_first_publication(file_path: Path) -> None:
    """
    Veri dosyasındaki ilk yayın kaydının temel yapısını inceler.
    """

    if not file_path.exists():
        print(f"Dosya bulunamadı: {file_path}")
        return

    publications = iter_publications(file_path)

    try:
        publication = next(publications)
    except StopIteration:
        print("Dosyada herhangi bir yayın kaydı bulunamadı.")
        return

    print("İlk yayın başarıyla okundu.")
    print(f"UID: {publication.get('UID')}")

    print_dict_keys(
        "Yayının üst seviye alanları:",
        publication,
    )

    static_data = publication.get("static_data", {})

    print_dict_keys(
        "static_data alanları:",
        static_data,
    )

    summary = (
        static_data.get("summary", {})
        if isinstance(static_data, dict)
        else {}
    )

    print_dict_keys(
        "static_data.summary alanları:",
        summary,
    )

    fullrecord_metadata = (
        static_data.get("fullrecord_metadata", {})
        if isinstance(static_data, dict)
        else {}
    )

    print_dict_keys(
        "static_data.fullrecord_metadata alanları:",
        fullrecord_metadata,
    )

    dynamic_data = publication.get("dynamic_data", {})

    print_dict_keys(
        "dynamic_data alanları:",
        dynamic_data,
    )

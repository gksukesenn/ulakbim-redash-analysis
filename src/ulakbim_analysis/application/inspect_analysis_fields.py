from pathlib import Path
from pprint import pprint
from typing import Any

from ulakbim_analysis.infrastructure.json_reader import iter_publications


def describe_value(title: str, value: Any) -> None:
    """
    Bir JSON alanının veri tipini ve temel yapısını gösterir.

    Büyük listeleri veya nesneleri tamamen ekrana basmaz.
    Yalnızca alanın yapısını anlamamıza yetecek kadar bilgi verir.
    """

    print(f"\n{title}")
    print(f"Tür: {type(value).__name__}")

    if isinstance(value, dict):
        print("Anahtarlar:")

        for key, child_value in value.items():
            if isinstance(child_value, dict):
                child_keys = list(child_value.keys())
                print(f"  - {key}: dict, anahtarlar={child_keys}")

            elif isinstance(child_value, list):
                print(f"  - {key}: list, eleman sayısı={len(child_value)}")

                if child_value:
                    first_item = child_value[0]

                    if isinstance(first_item, dict):
                        print(
                            "    İlk elemanın anahtarları: "
                            f"{list(first_item.keys())}"
                        )
                    else:
                        print(f"    İlk eleman: {first_item!r}")

            else:
                print(f"  - {key}: {child_value!r}")

    elif isinstance(value, list):
        print(f"Eleman sayısı: {len(value)}")

        if value:
            first_item = value[0]

            if isinstance(first_item, dict):
                print(
                    "İlk elemanın anahtarları: "
                    f"{list(first_item.keys())}"
                )
            else:
                print(f"İlk eleman: {first_item!r}")

    else:
        print(f"Değer: {value!r}")

def print_sample(title: str, value: Any) -> None:
    """
    Bir JSON alanının örnek içeriğini okunabilir biçimde gösterir.
    """

    print(f"\n{title}")
    pprint(value, width=100, sort_dicts=False)

def inspect_analysis_fields(file_path: Path) -> None:
    """
    İlk yayında analizlerde kullanılması muhtemel alanları inceler.
    """

    if not file_path.exists():
        print(f"Dosya bulunamadı: {file_path}")
        return

    try:
        publication = next(iter_publications(file_path))
    except StopIteration:
        print("Dosyada herhangi bir yayın kaydı bulunamadı.")
        return

    static_data = publication.get("static_data", {})

    if not isinstance(static_data, dict):
        print("static_data beklenen nesne yapısında değil.")
        return

    summary = static_data.get("summary", {})
    fullrecord_metadata = static_data.get("fullrecord_metadata", {})

    if not isinstance(summary, dict):
        summary = {}

    if not isinstance(fullrecord_metadata, dict):
        fullrecord_metadata = {}

    print("Analiz alanları inceleniyor.")
    print(f"UID: {publication.get('UID')}")

    describe_value(
        "Yayın bilgileri — pub_info",
        summary.get("pub_info"),
    )

    describe_value(
        "Yayıncı bilgileri — publishers",
        summary.get("publishers"),
    )

    describe_value(
        "Başlık ve dergi bilgileri — titles",
        summary.get("titles"),
    )

    describe_value(
        "Kurum ve adres bilgileri — addresses",
        fullrecord_metadata.get("addresses"),
    )

    describe_value(
        "Konu ve kategori bilgileri — category_info",
        fullrecord_metadata.get("category_info"),
    )

    describe_value(
        "Anahtar kelimeler — keywords",
        fullrecord_metadata.get("keywords"),
    )

    describe_value(
        "Dil bilgileri — languages",
        fullrecord_metadata.get("languages"),
    )

    describe_value(
        "Doküman türleri — doctypes",
        summary.get("doctypes"),
    )
    print_sample(
        "Yayıncı örnek verisi",
        summary.get("publishers"),
    )

    print_sample(
        "Başlık ve dergi örnek verisi",
        summary.get("titles"),
    )

    print_sample(
        "Kurum ve adres örnek verisi",
        fullrecord_metadata.get("addresses"),
    )

    print_sample(
        "Konu ve kategori örnek verisi",
        fullrecord_metadata.get("category_info"),
    )

from collections import Counter
from pathlib import Path
from typing import Any, Dict

from ulakbim_analysis.infrastructure.json_reader import iter_publications
from ulakbim_analysis.infrastructure.publication_mapper import map_publication


def validate_mapping(
    file_path: Path,
    limit: int = 1000,
) -> None:
    """
    Ham yayın kayıtlarını Publication modeline dönüştürür.

    Dönüşüm hatalarını ve analiz açısından önemli
    eksik alanların sayılarını raporlar.
    """

    statistics = Counter()
    displayed_error_count = 0

    for raw_publication in iter_publications(file_path):
        statistics["incelenen_kayit"] += 1

        try:
            publication = map_publication(raw_publication)
        except Exception as error:
            statistics["donusum_hatasi"] += 1

            if displayed_error_count < 5:
                uid = raw_publication.get("UID", "Bilinmiyor")

                print(
                    f"Dönüşüm hatası — UID: {uid} — "
                    f"{type(error).__name__}: {error}"
                )

                displayed_error_count += 1

            if statistics["incelenen_kayit"] >= limit:
                break

            continue

        statistics["basarili_donusum"] += 1

        if publication.uid == "UNKNOWN":
            statistics["eksik_uid"] += 1

        if publication.title is None:
            statistics["eksik_baslik"] += 1

        if publication.journal is None:
            statistics["eksik_dergi"] += 1

        if publication.publisher is None:
            statistics["eksik_yayinci"] += 1

        if publication.publication_year is None:
            statistics["eksik_yayin_yili"] += 1

        if publication.journal_gold_open_access is None:
            statistics["bilinmeyen_gold_oa"] += 1

        if publication.abstract is None:
            statistics["eksik_abstract"] += 1

        if publication.abstract_is_suspicious:
            statistics["supheli_abstract"] += 1

        actual_abstract_length = (
            len(publication.abstract)
            if publication.abstract is not None
            else 0
        )

        if publication.abstract_length != actual_abstract_length:
            statistics["abstract_uzunluk_hatasi"] += 1

        if not publication.institutions:
            statistics["eksik_kurum"] += 1

        if not publication.subjects:
            statistics["eksik_konu"] += 1

        if not publication.document_types:
            statistics["eksik_dokuman_turu"] += 1

        if not publication.languages:
            statistics["eksik_dil"] += 1

        if not publication.keywords:
            statistics["eksik_anahtar_kelime"] += 1

        if statistics["incelenen_kayit"] >= limit:
            break

    print("\nMapper doğrulama sonucu")
    print("------------------------")

    labels = {
        "incelenen_kayit": "İncelenen kayıt",
        "basarili_donusum": "Başarılı dönüşüm",
        "donusum_hatasi": "Dönüşüm hatası",
        "eksik_uid": "Eksik UID",
        "eksik_baslik": "Eksik başlık",
        "eksik_dergi": "Eksik dergi",
        "eksik_yayinci": "Eksik yayıncı",
        "eksik_yayin_yili": "Eksik yayın yılı",
        "bilinmeyen_gold_oa": "Bilinmeyen Gold OA",
        "eksik_kurum": "Eksik kurum",
        "eksik_konu": "Eksik konu",
        "eksik_dokuman_turu": "Eksik doküman türü",
        "eksik_dil": "Eksik dil",
        "eksik_anahtar_kelime": "Eksik anahtar kelime",
        "eksik_abstract": "Eksik abstract",
        "supheli_abstract": "Şüpheli abstract",
        "abstract_uzunluk_hatasi": "Abstract uzunluk hatası",
    }

    for key, label in labels.items():
        print(f"{label}: {statistics[key]}")


if __name__ == "__main__":
    validate_mapping(
        Path("data/raw/ulakbim_ubyt_wos_records.json")
    )

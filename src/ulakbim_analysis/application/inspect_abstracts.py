from collections import Counter
from pathlib import Path
from typing import Any, Dict

from ulakbim_analysis.domain.publication import (
    ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD,
)
from ulakbim_analysis.infrastructure.json_reader import iter_publications


DATA_FILE = Path("data/raw/ulakbim_ubyt_wos_records.json")


def get_abstract_fields(publication: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bir yayın kaydındaki abstract alanlarını güvenli biçimde döndürür.
    Alanlardan biri yoksa boş değer kullanır.
    """

    static_data = publication.get("static_data", {})
    summary = static_data.get("summary", {})
    pub_info = summary.get("pub_info", {})

    fullrecord_metadata = static_data.get("fullrecord_metadata", {})
    abstracts = fullrecord_metadata.get("abstracts", {})

    if not isinstance(abstracts, dict):
        abstracts = {}

    abstract = abstracts.get("abstract")

    if isinstance(abstract, dict):
        abstract_text = abstract.get("abstract_text")
    else:
        abstract_text = None

    if isinstance(abstract_text, dict):
        paragraph = abstract_text.get("p")
    else:
        paragraph = None

    return {
        "has_abstract": pub_info.get("has_abstract"),
        "abstract": abstract,
        "abstract_text": abstract_text,
        "paragraph": paragraph,
    }


def inspect_abstracts(limit: int = 1000) -> None:
    has_abstract_counts = Counter()
    abstract_type_counts = Counter()
    abstract_text_type_counts = Counter()
    paragraph_type_counts = Counter()

    text_lengths = []
    inspected_count = 0
    publications_with_text = 0
    publications_without_text = 0
    longest_abstract_length = 0
    longest_abstract_uid = None
    longest_abstract_preview = ""

    suspicious_abstracts = []

    for publication in iter_publications(DATA_FILE):
        inspected_count += 1
        fields = get_abstract_fields(publication)

        has_abstract = fields["has_abstract"]
        abstract = fields["abstract"]
        abstract_text = fields["abstract_text"]
        paragraph = fields["paragraph"]

        has_abstract_counts[str(has_abstract)] += 1
        abstract_type_counts[type(abstract).__name__] += 1
        abstract_text_type_counts[type(abstract_text).__name__] += 1
        paragraph_type_counts[type(paragraph).__name__] += 1

        if isinstance(paragraph, str):
            abstract_text = paragraph.strip()
        elif isinstance(paragraph, list):
            paragraph_parts = [
                item.strip()
                for item in paragraph
                if isinstance(item, str) and item.strip()
            ]
            abstract_text = " ".join(paragraph_parts)
        else:
            abstract_text = ""

        if abstract_text:
            publications_with_text += 1
            text_length = len(abstract_text)
            text_lengths.append(text_length)

            if text_length > ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD:
                suspicious_abstracts.append(
                    {
                        "uid": publication.get("UID"),
                        "length": text_length,
                        "paragraph_count": (
                            len(paragraph)
                            if isinstance(paragraph, list)
                            else 1
                        ),
                    }
                )

            if text_length > longest_abstract_length:
                longest_abstract_length = text_length
                longest_abstract_uid = publication.get("UID")
                longest_abstract_preview = abstract_text[:1000]
        else:
            publications_without_text += 1
        if inspected_count >= limit:
            break

    print(f"İncelenen yayın sayısı: {inspected_count}")

    print("\nhas_abstract değerleri:")
    for value, count in has_abstract_counts.most_common():
        print(f"  - {value!r}: {count}")

    print("\nabstract alanının veri tipleri:")
    for value_type, count in abstract_type_counts.most_common():
        print(f"  - {value_type}: {count}")

    print("\nabstract_text alanının veri tipleri:")
    for value_type, count in abstract_text_type_counts.most_common():
        print(f"  - {value_type}: {count}")

    print("\np alanının veri tipleri:")
    for value_type, count in paragraph_type_counts.most_common():
        print(f"  - {value_type}: {count}")

    print("\nGerçek abstract metni:")
    print(f"  - Metni bulunan: {publications_with_text}")
    print(f"  - Metni bulunmayan: {publications_without_text}")

    if text_lengths:
        print("\nAbstract uzunlukları:")
        print(f"  - En kısa: {min(text_lengths)} karakter")
        print(f"  - En uzun: {max(text_lengths)} karakter")
        print(
            f"  - Ortalama: "
            f"{sum(text_lengths) / len(text_lengths):.2f} karakter"
        )
        print("\nEn uzun abstract kaydı:")
        print(f"  - UID: {longest_abstract_uid}")
        print(f"  - Uzunluk: {longest_abstract_length} karakter")
        print(f"  - İlk 1000 karakter: {longest_abstract_preview!r}")
        print(
            "\n{0:,} karakteri aşan şüpheli abstractlar:".format(
                ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD
            )
        )
        print(f"  - Toplam: {len(suspicious_abstracts)}")

        for item in suspicious_abstracts:
            print(
                f"  - UID: {item['uid']}, "
                f"uzunluk: {item['length']}, "
                f"paragraf sayısı: {item['paragraph_count']}"
            )


if __name__ == "__main__":
    inspect_abstracts()

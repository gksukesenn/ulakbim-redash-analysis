from typing import Any, Dict, List, Optional

from ulakbim_analysis.domain.publication import Publication


def as_list(value: Any) -> List[Any]:
    """
    Tek değer veya liste olarak gelebilen alanları
    her zaman liste biçimine dönüştürür.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def as_dict(value: Any) -> Dict[str, Any]:
    """
    Değer sözlük değilse boş sözlük döndürür.
    """

    if isinstance(value, dict):
        return value

    return {}


def clean_text(value: Any) -> Optional[str]:
    """
    Metin değerinin başındaki ve sonundaki boşlukları temizler.

    Boş veya metin olmayan değerlerde None döndürür.
    """

    if not isinstance(value, str):
        return None

    cleaned_value = value.strip()

    if not cleaned_value:
        return None

    return cleaned_value


def unique_texts(values: List[str]) -> List[str]:
    """
    Metin listesindeki tekrarları sıralamayı bozmadan kaldırır.
    """

    unique_values = []
    seen_values = set()

    for value in values:
        if value not in seen_values:
            seen_values.add(value)
            unique_values.append(value)

    return unique_values


def extract_title_by_type(
    titles_data: Any,
    title_type: str,
) -> Optional[str]:
    """
    titles alanından belirtilen türdeki başlığı çıkarır.

    Örnek türler:
    - item: Makale başlığı
    - source: Dergi başlığı
    """

    titles = as_dict(titles_data)
    title_items = as_list(titles.get("title"))

    for title_item in title_items:
        title = as_dict(title_item)

        if title.get("type") != title_type:
            continue

        content = clean_text(title.get("content"))

        if content is not None:
            return content

    return None


def extract_publisher(publishers_data: Any) -> Optional[str]:
    """
    Yayıncı bilgisini standartlaştırılmış isim önceliğiyle çıkarır.
    """

    publishers = as_dict(publishers_data)
    publisher_items = as_list(publishers.get("publisher"))

    for publisher_item in publisher_items:
        publisher = as_dict(publisher_item)
        names = as_dict(publisher.get("names"))
        name_items = as_list(names.get("name"))

        for name_item in name_items:
            name = as_dict(name_item)

            candidate_fields = (
                "unified_name",
                "full_name",
                "display_name",
            )

            for field_name in candidate_fields:
                candidate = clean_text(name.get(field_name))

                if candidate is not None:
                    return candidate

    return None


def extract_institutions(addresses_data: Any) -> List[str]:
    """
    Adres kayıtlarından standartlaştırılmış kurum isimlerini çıkarır.
    """

    addresses = as_dict(addresses_data)
    address_items = as_list(addresses.get("address_name"))
    institutions = []

    for address_item in address_items:
        address = as_dict(address_item)
        address_spec = as_dict(address.get("address_spec"))
        organizations = as_dict(address_spec.get("organizations"))
        organization_items = as_list(
            organizations.get("organization")
        )

        preferred_names = []
        fallback_names = []

        for organization_item in organization_items:
            organization = as_dict(organization_item)
            content = clean_text(organization.get("content"))

            if content is None:
                continue

            if organization.get("pref") == "Y":
                preferred_names.append(content)
            else:
                fallback_names.append(content)

        if preferred_names:
            institutions.extend(preferred_names)
        elif fallback_names:
            institutions.append(fallback_names[0])

    return unique_texts(institutions)


def extract_subjects(category_info_data: Any) -> List[str]:
    """
    Konu ve kategori alanındaki subject değerlerini çıkarır.
    """

    category_info = as_dict(category_info_data)
    subjects_data = as_dict(category_info.get("subjects"))
    subject_items = as_list(subjects_data.get("subject"))
    subjects = []

    for subject_item in subject_items:
        if isinstance(subject_item, dict):
            subject = clean_text(subject_item.get("content"))
        else:
            subject = clean_text(subject_item)

        if subject is not None:
            subjects.append(subject)

    return unique_texts(subjects)


def extract_document_types(doctypes_data: Any) -> List[str]:
    """
    Tek metin veya liste olarak gelebilen doküman türlerini çıkarır.
    """

    doctypes = as_dict(doctypes_data)
    doctype_items = as_list(doctypes.get("doctype"))
    document_types = []

    for doctype_item in doctype_items:
        document_type = clean_text(doctype_item)

        if document_type is not None:
            document_types.append(document_type)

    return unique_texts(document_types)


def extract_languages(languages_data: Any) -> List[str]:
    """
    Yayının dil bilgilerini çıkarır.
    """

    languages = as_dict(languages_data)
    language_items = as_list(languages.get("language"))
    language_values = []

    for language_item in language_items:
        if isinstance(language_item, dict):
            language = clean_text(language_item.get("content"))
        else:
            language = clean_text(language_item)

        if language is not None:
            language_values.append(language)

    return unique_texts(language_values)


def extract_keywords(keywords_data: Any) -> List[str]:
    """
    Anahtar kelimeleri çıkarır.
    """

    keywords = as_dict(keywords_data)
    keyword_items = as_list(keywords.get("keyword"))
    keyword_values = []

    for keyword_item in keyword_items:
        if isinstance(keyword_item, dict):
            keyword = clean_text(keyword_item.get("content"))
        else:
            keyword = clean_text(keyword_item)

        if keyword is not None:
            keyword_values.append(keyword)

    return unique_texts(keyword_values)


def parse_publication_year(value: Any) -> Optional[int]:
    """
    Yayın yılını tam sayıya dönüştürür.
    """

    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None

    return None


def parse_gold_open_access(value: Any) -> Optional[bool]:
    """
    journal_oas_gold alanındaki Y/N değerini boolean'a dönüştürür.
    """

    if not isinstance(value, str):
        return None

    normalized_value = value.strip().upper()

    if normalized_value == "Y":
        return True

    if normalized_value == "N":
        return False

    return None


def map_publication(raw_publication: Dict[str, Any]) -> Publication:
    """
    Ham Web of Science kaydını sade Publication modeline dönüştürür.
    """

    static_data = as_dict(raw_publication.get("static_data"))
    summary = as_dict(static_data.get("summary"))
    fullrecord_metadata = as_dict(
        static_data.get("fullrecord_metadata")
    )
    pub_info = as_dict(summary.get("pub_info"))

    uid = clean_text(raw_publication.get("UID"))

    if uid is None:
        uid = "UNKNOWN"

    return Publication(
        uid=uid,
        title=extract_title_by_type(
            summary.get("titles"),
            "item",
        ),
        journal=extract_title_by_type(
            summary.get("titles"),
            "source",
        ),
        publisher=extract_publisher(
            summary.get("publishers")
        ),
        publication_year=parse_publication_year(
            pub_info.get("pubyear")
        ),
        journal_gold_open_access=parse_gold_open_access(
            pub_info.get("journal_oas_gold")
        ),
        institutions=extract_institutions(
            fullrecord_metadata.get("addresses")
        ),
        subjects=extract_subjects(
            fullrecord_metadata.get("category_info")
        ),
        document_types=extract_document_types(
            summary.get("doctypes")
        ),
        languages=extract_languages(
            fullrecord_metadata.get("languages")
        ),
        keywords=extract_keywords(
            fullrecord_metadata.get("keywords")
        ),
    )

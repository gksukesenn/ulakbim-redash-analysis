from typing import Any, Dict

import pytest

from ulakbim_analysis.infrastructure.publication_mapper import (
    as_list,
    clean_text,
    extract_document_types,
    extract_abstract,
    extract_institutions,
    extract_keywords,
    extract_languages,
    extract_publisher,
    extract_subjects,
    extract_title_by_type,
    map_publication,
    parse_gold_open_access,
    parse_publication_year,
    unique_texts,
)
from ulakbim_analysis.domain.publication import (
    ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD,
)


def test_as_list_normalizes_values() -> None:
    assert as_list(None) == []
    assert as_list("value") == ["value"]
    assert as_list(["value"]) == ["value"]


def test_clean_text_handles_invalid_and_empty_values() -> None:
    assert clean_text("  text  ") == "text"
    assert clean_text("  ") is None
    assert clean_text(10) is None


def test_unique_texts_preserves_order() -> None:
    assert unique_texts(["a", "b", "a"]) == ["a", "b"]


def test_extract_title_by_type() -> None:
    titles = {
        "title": [
            {"type": "item", "content": "Article"},
            {"type": "source", "content": "Journal"},
        ]
    }
    assert extract_title_by_type(titles, "item") == "Article"
    assert extract_title_by_type(titles, "source") == "Journal"


def test_extract_publisher_uses_defined_priority() -> None:
    publishers = {
        "publisher": {
            "names": {
                "name": {
                    "display_name": "Display",
                    "full_name": "Full",
                    "unified_name": "Unified",
                }
            }
        }
    }
    assert extract_publisher(publishers) == "Unified"


def test_extract_institutions_prefers_standard_names() -> None:
    addresses = {
        "address_name": [
            {
                "address_spec": {
                    "organizations": {
                        "organization": [
                            {"pref": "N", "content": "Department"},
                            {"pref": "Y", "content": "University"},
                        ]
                    }
                }
            },
            {
                "address_spec": {
                    "organizations": {
                        "organization": {"content": "Institute"}
                    }
                }
            },
        ]
    }
    assert extract_institutions(addresses) == ["University", "Institute"]


def test_extract_subjects_supports_dict_and_string() -> None:
    value = {
        "subjects": {
            "subject": [{"content": "Physics"}, "Chemistry", "Physics"]
        }
    }
    assert extract_subjects(value) == ["Physics", "Chemistry"]


def test_extract_document_types_supports_single_and_list() -> None:
    assert extract_document_types({"doctype": "Article"}) == ["Article"]
    assert extract_document_types(
        {"doctype": ["Article", "Review"]}
    ) == ["Article", "Review"]


def test_extract_languages_supports_dict_and_string() -> None:
    value = {
        "language": [{"content": "English"}, "Turkish", "English"]
    }
    assert extract_languages(value) == ["English", "Turkish"]


def test_extract_keywords_supports_dict_and_string() -> None:
    value = {"keyword": ["data", {"content": "streaming"}, "data"]}
    assert extract_keywords(value) == ["data", "streaming"]


def test_extract_abstract_supports_single_paragraph() -> None:
    value = {"abstract": {"abstract_text": {"p": "  Tek paragraf.  "}}}

    assert extract_abstract(value) == "Tek paragraf."


def test_extract_abstract_supports_paragraph_list() -> None:
    value = {
        "abstract": {
            "abstract_text": {"p": [" İlk paragraf. ", "İkinci paragraf."]}
        }
    }

    assert extract_abstract(value) == "İlk paragraf. İkinci paragraf."


@pytest.mark.parametrize(
    "value, expected",
    [
        (2024, 2024),
        (" 2023 ", 2023),
        (True, None),
        ("unknown", None),
        (None, None),
    ],
)
def test_parse_publication_year(value: Any, expected: Any) -> None:
    assert parse_publication_year(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Y", True),
        (" n ", False),
        ("unknown", None),
        (True, None),
        (None, None),
    ],
)
def test_parse_gold_open_access(value: Any, expected: Any) -> None:
    assert parse_gold_open_access(value) is expected


def test_map_publication(raw_publication: Dict[str, Any]) -> None:
    publication = map_publication(raw_publication)

    assert publication.uid == "WOS:TEST-1"
    assert publication.title == "Test Article"
    assert publication.journal == "Test Journal"
    assert publication.publisher == "Test Publisher"
    assert publication.publication_year == 2024
    assert publication.journal_gold_open_access is True
    assert publication.institutions == ["Test University"]
    assert publication.subjects == ["Engineering"]
    assert publication.document_types == ["Article", "Review"]
    assert publication.languages == ["English"]
    assert publication.keywords == ["data", "streaming"]


def _set_abstract(raw_publication: Dict[str, Any], paragraph: Any) -> None:
    metadata = raw_publication["static_data"]["fullrecord_metadata"]
    metadata["abstracts"] = {
        "abstract": {"abstract_text": {"p": paragraph}}
    }


def test_map_publication_without_abstract(
    raw_publication: Dict[str, Any],
) -> None:
    publication = map_publication(raw_publication)

    assert publication.abstract is None
    assert publication.abstract_length == 0
    assert publication.abstract_is_suspicious is False


@pytest.mark.parametrize(
    "length, expected_suspicious",
    [
        (ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD, False),
        (ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD + 1, True),
    ],
)
def test_map_publication_abstract_suspicious_boundary(
    raw_publication: Dict[str, Any],
    length: int,
    expected_suspicious: bool,
) -> None:
    _set_abstract(raw_publication, "a" * length)

    publication = map_publication(raw_publication)

    assert publication.abstract is not None
    assert publication.abstract_length == len(publication.abstract)
    assert publication.abstract_length == length
    assert publication.abstract_is_suspicious is expected_suspicious

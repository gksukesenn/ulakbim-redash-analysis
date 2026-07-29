from typing import Any, Dict

import pytest


@pytest.fixture
def raw_publication() -> Dict[str, Any]:
    """Mapper testlerinde kullanılan küçük Web of Science kaydı."""

    return {
        "UID": "WOS:TEST-1",
        "static_data": {
            "summary": {
                "pub_info": {
                    "pubyear": "2024",
                    "journal_oas_gold": "Y",
                },
                "publishers": {
                    "publisher": {
                        "names": {
                            "name": {
                                "unified_name": "Test Publisher",
                                "full_name": "Test Publisher Full",
                            }
                        }
                    }
                },
                "titles": {
                    "title": [
                        {"type": "item", "content": " Test Article "},
                        {"type": "source", "content": "Test Journal"},
                    ]
                },
                "doctypes": {"doctype": ["Article", "Review"]},
            },
            "fullrecord_metadata": {
                "addresses": {
                    "address_name": {
                        "address_spec": {
                            "organizations": {
                                "organization": [
                                    {"pref": "N", "content": "Department"},
                                    {"pref": "Y", "content": "Test University"},
                                ]
                            }
                        }
                    }
                },
                "category_info": {
                    "subjects": {
                        "subject": [
                            {"content": "Engineering"},
                            {"content": "Engineering"},
                        ]
                    }
                },
                "languages": {
                    "language": {"content": "English"}
                },
                "keywords": {
                    "keyword": ["data", {"content": "streaming"}]
                },
            },
        },
    }

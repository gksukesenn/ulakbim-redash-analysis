from typing import Any, Dict

from ulakbim_analysis.application.analyze_all_abstracts import (
    DISTRIBUTION_LABELS,
    analyze_abstract_records,
)
from ulakbim_analysis.domain.publication import (
    ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD,
    Publication,
)


def test_analysis_calculates_statistics_and_continues_after_error() -> None:
    records = [
        {"UID": "MISSING"},
        {"UID": "SHORT"},
        {"UID": "LONG"},
        {"UID": "SUSPICIOUS"},
        {"UID": "BROKEN"},
    ]

    def mapper(raw: Dict[str, Any]) -> Publication:
        uid = raw["UID"]
        if uid == "BROKEN":
            raise TypeError("bozuk kayıt")
        lengths = {
            "MISSING": 0,
            "SHORT": 100,
            "LONG": 2_000,
            "SUSPICIOUS": ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD + 1,
        }
        length = lengths[uid]
        return Publication(
            uid=uid,
            abstract=None if length == 0 else "a" * length,
            abstract_length=length,
            abstract_is_suspicious=(
                length > ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD
            ),
        )

    result = analyze_abstract_records(
        records,
        mapper=mapper,
        progress_interval=2,
    )

    assert result.inspected == 5
    assert result.successful == 4
    assert result.mapping_errors == 1
    assert result.with_abstract == 3
    assert result.without_abstract == 1
    assert result.suspicious_count == 1
    assert result.shortest_normal_length == 100
    assert result.longest_normal_length == 2_000
    assert result.average_normal_length == 1_050
    assert result.median_normal_length == 1_050
    assert result.distribution[DISTRIBUTION_LABELS[0]] == 1
    assert result.distribution[DISTRIBUTION_LABELS[1]] == 1
    assert result.distribution[DISTRIBUTION_LABELS[2]] == 1
    assert result.distribution[DISTRIBUTION_LABELS[5]] == 1
    assert result.errors[0].uid == "BROKEN"
    assert result.errors[0].error_type == "TypeError"


def test_analysis_keeps_at_most_five_errors() -> None:
    records = [{"UID": str(index)} for index in range(7)]

    def broken_mapper(raw: Dict[str, Any]) -> Publication:
        raise ValueError(raw["UID"])

    result = analyze_abstract_records(
        records,
        mapper=broken_mapper,
        progress_interval=10,
    )

    assert result.mapping_errors == 7
    assert len(result.errors) == 5

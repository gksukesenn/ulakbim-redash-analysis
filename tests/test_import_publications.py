from typing import Any, Dict, List

import pytest

from ulakbim_analysis.application.import_publications import (
    import_publication_records,
)
from ulakbim_analysis.application.publication_repository import (
    RepositoryWriteResult,
)
from ulakbim_analysis.domain.publication import Publication


class FakeRepository:
    """UID tabanlı davranan, MongoDB gerektirmeyen test deposu."""

    def __init__(self) -> None:
        self.documents: Dict[str, Publication] = {}
        self.batch_sizes: List[int] = []

    def upsert_publications(
        self,
        publications: List[Publication],
    ) -> RepositoryWriteResult:
        self.batch_sizes.append(len(publications))
        matched = 0
        modified = 0
        upserted = 0
        for publication in publications:
            previous = self.documents.get(publication.uid)
            if previous is None:
                upserted += 1
            else:
                matched += 1
                if previous != publication:
                    modified += 1
            self.documents[publication.uid] = publication
        return RepositoryWriteResult(
            matched=matched,
            modified=modified,
            upserted=upserted,
        )


def make_records(count: int) -> List[Dict[str, Any]]:
    return [{"UID": "WOS:{0}".format(index)} for index in range(count)]


def test_import_writes_at_batch_boundaries() -> None:
    repository = FakeRepository()

    result = import_publication_records(
        make_records(5),
        repository,
        batch_size=2,
    )

    assert repository.batch_sizes == [2, 2, 1]
    assert result.inspected == 5
    assert result.successful == 5
    assert result.upserted == 5
    assert result.written == 5


def test_import_limit_stops_stream() -> None:
    repository = FakeRepository()
    result = import_publication_records(
        make_records(5),
        repository,
        limit=3,
        batch_size=2,
    )

    assert result.inspected == 3
    assert len(repository.documents) == 3


def test_import_limit_does_not_consume_extra_record() -> None:
    repository = FakeRepository()
    consumed: List[str] = []

    def records() -> Any:
        for index in range(5):
            uid = "WOS:{0}".format(index)
            consumed.append(uid)
            yield {"UID": uid}

    import_publication_records(
        records(),
        repository,
        limit=2,
    )

    assert consumed == ["WOS:0", "WOS:1"]


@pytest.mark.parametrize(
    "limit, batch_size",
    [(0, 1), (-1, 1), (None, 0), (None, -1)],
)
def test_import_rejects_non_positive_options(
    limit: Any,
    batch_size: int,
) -> None:
    with pytest.raises(ValueError):
        import_publication_records(
            [],
            FakeRepository(),
            limit=limit,
            batch_size=batch_size,
        )


def test_import_skips_unknown_uid() -> None:
    repository = FakeRepository()
    result = import_publication_records(
        [{"UID": "  "}],
        repository,
    )

    assert result.inspected == 1
    assert result.successful == 0
    assert result.skipped == 1
    assert repository.documents == {}


def test_mapping_error_does_not_stop_other_records() -> None:
    repository = FakeRepository()

    def mapper(raw: Dict[str, Any]) -> Publication:
        if raw["UID"] == "BROKEN":
            raise TypeError("bozuk kayıt")
        return Publication(uid=raw["UID"])

    result = import_publication_records(
        [{"UID": "ONE"}, {"UID": "BROKEN"}, {"UID": "TWO"}],
        repository,
        mapper=mapper,
    )

    assert result.inspected == 3
    assert result.successful == 2
    assert result.mapping_errors == 1
    assert set(repository.documents) == {"ONE", "TWO"}
    assert result.errors[0].uid == "BROKEN"
    assert result.errors[0].error_type == "TypeError"


def test_second_import_does_not_create_duplicates() -> None:
    repository = FakeRepository()
    records = make_records(3)

    first_result = import_publication_records(records, repository)
    second_result = import_publication_records(records, repository)

    assert first_result.written == 3
    assert first_result.upserted == 3
    assert second_result.written == 0
    assert second_result.matched == 3
    assert second_result.modified == 0
    assert second_result.upserted == 0
    assert len(repository.documents) == 3


def test_second_import_reports_modified_document() -> None:
    repository = FakeRepository()

    import_publication_records([{"UID": "ONE"}], repository)
    result = import_publication_records(
        [{"UID": "ONE"}],
        repository,
        mapper=lambda raw: Publication(
            uid=raw["UID"],
            title="Updated",
        ),
    )

    assert result.matched == 1
    assert result.modified == 1
    assert result.upserted == 0
    assert result.written == 1

from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from time import monotonic
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
)

from ulakbim_analysis.application.publication_repository import (
    PublicationRepository,
    RepositoryWriteResult,
)
from ulakbim_analysis.domain.publication import Publication
from ulakbim_analysis.infrastructure.json_reader import iter_publications
from ulakbim_analysis.infrastructure.publication_mapper import map_publication


@dataclass(frozen=True)
class ImportErrorInfo:
    """Kullanıcıya gösterilebilecek sınırlı kayıt dönüşüm hatası."""

    uid: str
    error_type: str
    message: str


@dataclass
class ImportResult:
    """Bir import çalışmasının sayaç ve süre sonucu."""

    inspected: int = 0
    successful: int = 0
    skipped: int = 0
    mapping_errors: int = 0
    matched: int = 0
    modified: int = 0
    upserted: int = 0
    written: int = 0
    duration_seconds: float = 0.0
    errors: List[ImportErrorInfo] = field(default_factory=list)


def _validate_options(
    limit: Optional[int],
    batch_size: int,
) -> None:
    if limit is not None and limit <= 0:
        raise ValueError("limit pozitif olmalıdır.")
    if batch_size <= 0:
        raise ValueError("batch_size pozitif olmalıdır.")


def _write_batch(
    repository: PublicationRepository,
    batch: List[Publication],
) -> RepositoryWriteResult:
    if not batch:
        return RepositoryWriteResult()

    write_result = repository.upsert_publications(batch)
    batch.clear()
    return write_result


def _add_write_result(
    import_result: ImportResult,
    write_result: RepositoryWriteResult,
) -> None:
    import_result.matched += write_result.matched
    import_result.modified += write_result.modified
    import_result.upserted += write_result.upserted
    import_result.written += write_result.written


def import_publication_records(
    raw_publications: Iterable[Dict[str, Any]],
    repository: PublicationRepository,
    limit: Optional[int] = None,
    batch_size: int = 500,
    mapper: Callable[[Dict[str, Any]], Publication] = map_publication,
    max_displayed_errors: int = 5,
) -> ImportResult:
    """Ham kayıt akışını sınırlı batch'lerle repository'ye aktarır."""

    _validate_options(limit, batch_size)
    if max_displayed_errors < 0:
        raise ValueError("max_displayed_errors negatif olamaz.")

    result = ImportResult()
    batch: List[Publication] = []
    started_at = monotonic()

    selected_publications = (
        raw_publications
        if limit is None
        else islice(raw_publications, limit)
    )

    for raw_publication in selected_publications:
        result.inspected += 1
        try:
            publication = mapper(raw_publication)
        except Exception as error:
            result.mapping_errors += 1
            if len(result.errors) < max_displayed_errors:
                uid = raw_publication.get("UID", "Bilinmiyor")
                result.errors.append(
                    ImportErrorInfo(
                        uid=str(uid),
                        error_type=type(error).__name__,
                        message=str(error),
                    )
                )
            continue

        if publication.uid == "UNKNOWN":
            result.skipped += 1
            continue

        result.successful += 1
        batch.append(publication)

        if len(batch) >= batch_size:
            _add_write_result(
                result,
                _write_batch(repository, batch),
            )

    _add_write_result(result, _write_batch(repository, batch))
    result.duration_seconds = monotonic() - started_at
    return result


def import_publications(
    file_path: Path,
    repository: PublicationRepository,
    limit: Optional[int] = None,
    batch_size: int = 500,
) -> ImportResult:
    """JSON dosyasındaki yayınları streaming biçimde içe aktarır."""

    return import_publication_records(
        raw_publications=iter_publications(file_path),
        repository=repository,
        limit=limit,
        batch_size=batch_size,
    )

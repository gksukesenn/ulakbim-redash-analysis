from dataclasses import dataclass
from typing import List, Protocol

from ulakbim_analysis.domain.publication import Publication


@dataclass(frozen=True)
class RepositoryWriteResult:
    """Repository batch yazımının teknoloji bağımsız sayaçları."""

    matched: int = 0
    modified: int = 0
    upserted: int = 0

    @property
    def written(self) -> int:
        """Yeni eklenen ve içeriği değişen belge toplamı."""

        return self.upserted + self.modified


class PublicationRepository(Protocol):
    """Import kullanım senaryosunun ihtiyaç duyduğu küçük depo sözleşmesi."""

    def upsert_publications(
        self,
        publications: List[Publication],
    ) -> RepositoryWriteResult:
        ...

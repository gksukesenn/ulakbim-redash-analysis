from dataclasses import dataclass, field
from typing import List, Optional


ABSTRACT_SUSPICIOUS_LENGTH_THRESHOLD = 10_000


@dataclass
class Publication:
    """
    Analiz sisteminde kullanılan sadeleştirilmiş yayın modeli.

    Ham Web of Science JSON yapısını değil, MongoDB ve Redash
    analizlerinde ihtiyaç duyacağımız temiz alanları temsil eder.
    """

    uid: str

    title: Optional[str] = None
    journal: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    journal_gold_open_access: Optional[bool] = None
    abstract: Optional[str] = None
    abstract_length: int = 0
    abstract_is_suspicious: bool = False

    institutions: List[str] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)
    document_types: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

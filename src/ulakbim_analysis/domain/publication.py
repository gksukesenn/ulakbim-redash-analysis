from dataclasses import dataclass, field
from typing import List, Optional


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

    institutions: List[str] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)
    document_types: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

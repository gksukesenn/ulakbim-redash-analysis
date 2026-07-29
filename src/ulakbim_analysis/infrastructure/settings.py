import os
from dataclasses import dataclass
from typing import Mapping, Optional

from dotenv import load_dotenv


DEFAULT_DATABASE = "ulakbim_analysis"
DEFAULT_COLLECTION = "publications"
DEFAULT_CONNECT_TIMEOUT_MS = 5000


@dataclass(frozen=True)
class MongoDBSettings:
    """MongoDB bağlantısı için ortam tabanlı yapılandırma."""

    uri: str
    database: str = DEFAULT_DATABASE
    collection: str = DEFAULT_COLLECTION
    connect_timeout_ms: int = DEFAULT_CONNECT_TIMEOUT_MS

    @classmethod
    def from_env(
        cls,
        environ: Optional[Mapping[str, str]] = None,
    ) -> "MongoDBSettings":
        """Ayarları `.env` ve ortam değişkenlerinden oluşturur."""

        if environ is None:
            load_dotenv()
            values = os.environ
        else:
            values = environ

        uri = values.get("MONGODB_URI", "").strip()
        if not uri:
            raise ValueError(
                "MONGODB_URI tanımlı değil. .env.example dosyasını temel "
                "alarak .env oluşturun."
            )

        database = values.get(
            "MONGODB_DATABASE",
            DEFAULT_DATABASE,
        ).strip()
        collection = values.get(
            "MONGODB_COLLECTION",
            DEFAULT_COLLECTION,
        ).strip()

        if not database:
            raise ValueError("MONGODB_DATABASE boş olamaz.")
        if not collection:
            raise ValueError("MONGODB_COLLECTION boş olamaz.")

        timeout_text = values.get(
            "MONGODB_CONNECT_TIMEOUT_MS",
            str(DEFAULT_CONNECT_TIMEOUT_MS),
        )
        try:
            timeout = int(timeout_text)
        except ValueError:
            raise ValueError("MONGODB_CONNECT_TIMEOUT_MS tam sayı olmalıdır.")

        if timeout <= 0:
            raise ValueError("MONGODB_CONNECT_TIMEOUT_MS pozitif olmalıdır.")

        return cls(
            uri=uri,
            database=database,
            collection=collection,
            connect_timeout_ms=timeout,
        )

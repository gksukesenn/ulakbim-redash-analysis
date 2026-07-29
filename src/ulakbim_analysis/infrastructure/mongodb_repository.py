from dataclasses import asdict
from typing import List, Optional

from pymongo import ASCENDING, MongoClient, UpdateOne
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from ulakbim_analysis.application.publication_repository import (
    RepositoryWriteResult,
)
from ulakbim_analysis.domain.publication import Publication
from ulakbim_analysis.infrastructure.settings import MongoDBSettings


class MongoDBRepository:
    """Sadeleştirilmiş yayın belgelerinin MongoDB deposu."""

    def __init__(
        self,
        settings: MongoDBSettings,
        client: Optional[MongoClient] = None,
    ) -> None:
        self._client = client or MongoClient(
            settings.uri,
            serverSelectionTimeoutMS=settings.connect_timeout_ms,
            connectTimeoutMS=settings.connect_timeout_ms,
        )
        self._collection: Collection = self._client[
            settings.database
        ][settings.collection]

    def check_connection(self) -> None:
        """Sunucu bağlantısını kısa bir ping işlemiyle doğrular."""

        try:
            self._client.admin.command("ping")
        except PyMongoError as error:
            raise ConnectionError(
                "MongoDB bağlantısı kurulamadı: {0}".format(error)
            )

    def ensure_indexes(self) -> None:
        """UID alanı için unique index oluşturur."""

        self._collection.create_index(
            [("uid", ASCENDING)],
            unique=True,
            name="uid_unique",
        )

    def upsert_publications(
        self,
        publications: List[Publication],
    ) -> RepositoryWriteResult:
        """Yayınları UID üzerinden toplu ve idempotent biçimde yazar."""

        if not publications:
            return RepositoryWriteResult()

        operations = [
            UpdateOne(
                {"uid": publication.uid},
                {"$set": asdict(publication)},
                upsert=True,
            )
            for publication in publications
        ]
        result = self._collection.bulk_write(operations, ordered=False)
        return RepositoryWriteResult(
            matched=result.matched_count,
            modified=result.modified_count,
            upserted=result.upserted_count,
        )

    def count(self) -> int:
        """Collection içindeki toplam yayın sayısını döndürür."""

        return self._collection.count_documents({})

    def close(self) -> None:
        """MongoDB istemcisini kapatır."""

        self._client.close()

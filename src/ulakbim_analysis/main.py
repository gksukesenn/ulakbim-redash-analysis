import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from ulakbim_analysis.application.import_publications import (
    ImportResult,
    import_publications,
)
from ulakbim_analysis.application.inspect_dataset import (
    inspect_first_publication,
)
from ulakbim_analysis.application.validate_mapping import validate_mapping
from ulakbim_analysis.infrastructure.mongodb_repository import (
    MongoDBRepository,
)
from ulakbim_analysis.infrastructure.settings import MongoDBSettings


DEFAULT_DATA_FILE = Path(
    "data/raw/ulakbim_ubyt_wos_records.json"
)


def positive_integer(value: str) -> int:
    """Argparse için pozitif tam sayı doğrulayıcısı."""

    try:
        parsed_value = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("pozitif bir tam sayı olmalıdır")

    if parsed_value <= 0:
        raise argparse.ArgumentTypeError("pozitif bir tam sayı olmalıdır")
    return parsed_value


def build_parser() -> argparse.ArgumentParser:
    """Uygulamanın terminal argümanlarını oluşturur."""

    parser = argparse.ArgumentParser(
        description="ULAKBİM yayın verisi analiz araçları"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Ham verideki ilk yayının yapısını gösterir.",
    )
    inspect_parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_DATA_FILE,
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Mapper sonuçlarını örnek kayıtlarla doğrular.",
    )
    validate_parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_DATA_FILE,
    )
    validate_parser.add_argument(
        "--limit",
        type=positive_integer,
        default=1000,
    )

    import_parser = subparsers.add_parser(
        "import",
        help="Yayınları streaming biçimde MongoDB'ye aktarır.",
    )
    import_parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_DATA_FILE,
    )
    import_parser.add_argument(
        "--limit",
        type=positive_integer,
        default=None,
    )
    import_parser.add_argument(
        "--batch-size",
        type=positive_integer,
        default=500,
    )

    subparsers.add_parser(
        "count",
        help="MongoDB collection kayıt sayısını gösterir.",
    )
    return parser


def _print_import_result(result: ImportResult) -> None:
    print("Import sonucu")
    print("--------------")
    print("İncelenen kayıt: {0}".format(result.inspected))
    print("Başarılı dönüşüm: {0}".format(result.successful))
    print("Atlanan kayıt: {0}".format(result.skipped))
    print("Dönüşüm hatası: {0}".format(result.mapping_errors))
    print("Eşleşen mevcut kayıt: {0}".format(result.matched))
    print("Yeni eklenen kayıt: {0}".format(result.upserted))
    print("İçeriği değiştirilen kayıt: {0}".format(result.modified))
    print("Yazılan/değiştirilen kayıt: {0}".format(result.written))
    print("Toplam süre: {0:.2f} saniye".format(result.duration_seconds))

    for error in result.errors:
        print(
            "Hata — UID: {0} — {1}: {2}".format(
                error.uid,
                error.error_type,
                error.message,
            )
        )


def _create_repository() -> MongoDBRepository:
    settings = MongoDBSettings.from_env()
    repository = MongoDBRepository(settings)
    try:
        repository.check_connection()
    except ConnectionError:
        repository.close()
        raise
    return repository


def _run_import(args: argparse.Namespace) -> None:
    repository = _create_repository()
    try:
        repository.ensure_indexes()
        result = import_publications(
            file_path=args.file,
            repository=repository,
            limit=args.limit,
            batch_size=args.batch_size,
        )
        _print_import_result(result)
        print("MongoDB toplam kayıt: {0}".format(repository.count()))
    finally:
        repository.close()


def _run_count() -> None:
    repository = _create_repository()
    try:
        print("MongoDB yayın sayısı: {0}".format(repository.count()))
    finally:
        repository.close()


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI komutunu çalıştırır ve süreç çıkış kodunu döndürür."""

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "inspect":
            inspect_first_publication(args.file)
        elif args.command == "validate":
            validate_mapping(args.file, args.limit)
        elif args.command == "import":
            _run_import(args)
        elif args.command == "count":
            _run_count()
    except (ConnectionError, OSError, ValueError) as error:
        print("Hata: {0}".format(error), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

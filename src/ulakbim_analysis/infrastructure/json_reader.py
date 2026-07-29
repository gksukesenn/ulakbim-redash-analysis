from pathlib import Path
from typing import Any, Dict, Iterator

import ijson


PUBLICATION_PREFIX = "item.Data.Records.records.REC.item"


def iter_publications(file_path: Path) -> Iterator[Dict[str, Any]]:
    """
    Büyük JSON dosyasındaki yayın kayıtlarını sırayla üretir.

    Dosyanın tamamını belleğe yüklemez. Her seferinde yalnızca
    bir yayın kaydını okuyarak çağıran koda gönderir.
    """
    with file_path.open("rb") as json_file:
        publications = ijson.items(json_file, PUBLICATION_PREFIX)

        for publication in publications:
            if isinstance(publication, dict):
                yield publication

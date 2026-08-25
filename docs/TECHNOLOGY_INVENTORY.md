# Teknoloji envanteri

## Doğrudan ve dolaylı teknolojiler

| Teknoloji | Projedeki gerçek görevi | Kullanıldığı dosyalar | Tür | Zorunlu mu? |
|---|---|---|---|---|
| Python 3.8+ | Bütün ETL, CLI, embedding orchestration, clustering ve test kodu | `src/**/*.py`, `tests/**/*.py`, `pyproject.toml` | Çalışma + geliştirme | Evet |
| dataclasses / typing Protocol | Domain DTO'ları ve teknoloji bağımsız port sözleşmeleri | `domain/*.py`, `publication_repository.py`, `vector_experiment.py` | Stdlib runtime | Evet |
| ijson | 744 MB JSON'u `item.Data.Records.records.REC.item` path'inde streaming parse eder | `json_reader.py`, `pyproject.toml` | Runtime | Mongo/raw akışı için evet |
| PyMongo | Mongo client, unique index, unordered bulk `UpdateOne` upsert ve count | `mongodb_repository.py` | Runtime | Mongo akışı için evet |
| MongoDB 7.0.14 | Normalize `Publication` belgelerinin kalıcı analiz deposu | `docker-compose.yml`, `settings.py`, Redash JSON'ları | Runtime servis | A alanı için evet |
| Redash 26.3.0 | MongoDB aggregation sonuçlarını sorgu/grafik/dashboard olarak sunar | `docker-compose.yml`, `docs/redash_queries/*`, `README.md` | Runtime servis/UI | Dashboard için evet |
| PostgreSQL 17 | Bilimsel makaleleri değil Redash kullanıcı, data source, query, visualization ve dashboard metadata'sını tutar | `docker-compose.yml:38-53`, `REDASH_DATABASE_URL` | Redash altyapısı | Redash için evet |
| Redis 7 | Makale verisi tutmaz; Redash task/query queue koordinasyonu | `docker-compose.yml:55-68,103-134` | Redash altyapısı | Redash için evet |
| Docker | MongoDB, Redash stack ve Qdrant servislerini izole çalıştırır | iki Compose dosyası, README | Runtime/operasyon | Belgelenen kurulum için evet; Python kodu teorik olarak harici servis kullanabilir |
| Docker Compose | Servis, healthcheck, port ve named volume tanımları | `docker-compose.yml`, `docker-compose.vector-experiment.yml` | Operasyon | Belgelenen yerel kurulum için evet |
| Qdrant 1.15.4 server | 384 boyutlu vektör/payload saklama, cosine nearest-neighbor query ve scroll | vector Compose, `qdrant_vector_store.py` | Runtime servis | B alanı için evet |
| qdrant-client | Python Qdrant adapter SDK'sı | `qdrant_vector_store.py`, `pyproject.toml` vector/cluster extra | Runtime | B alanı için evet |
| FastEmbed 0.3–<0.6 | Hazır sentence-transformer modelini ONNX Runtime ile çağıran adapter | `local_embedding.py`, `pyproject.toml` | Runtime optional | Yeni query/load için evet; yalnız mevcut clustering için hayır |
| sentence-transformers model kimliği | `paraphrase-multilingual-MiniLM-L12-v2` hazır ağı; eğitim yok | `vector_settings.py`, `.env.example`, similarity report | Model artifact/config | Embedding üretimi için evet |
| Hugging Face Hub | FastEmbed'in model edinme/cache bağımlılık zincirinde kurulu (`huggingface_hub`); proje doğrudan API çağırmaz veya cache path ayarlamaz | Doğrudan repository importu yok; kurulu FastEmbed transitive bağımlılığı | Dolaylı runtime | Model ilk edinimi/cache çözümü için FastEmbed'e bağlı |
| ONNX / ONNX Runtime | FastEmbed model inference backend'i; repository doğrudan import etmez | FastEmbed üzerinden; `local_embedding.py` docstring | Dolaylı runtime | FastEmbed inference için evet |
| NumPy | FastEmbed vektör çıktısı ve sklearn/matplotlib sayısal altyapısı; proje çıktı üzerinde yalnız `.tolist()` çağırır | `local_embedding.py`; transitive dependency | Dolaylı runtime | Embedding/clustering için evet |
| scikit-learn 1.3–<2 | `PCA(n_components=2)` ve `KMeans(k=3)` | `cluster_article_vectors.py`, cluster extra | Runtime optional | Kümeleme için evet |
| matplotlib 3.7–<4 | Headless `Agg` backend ile PNG scatter üretir | `cluster_article_vectors.py`, cluster extra | Runtime optional | PNG için evet |
| SciPy / joblib / threadpoolctl | scikit-learn'in kurulu dolaylı bağımlılıkları; proje doğrudan kullanmaz | Repository importu yok | Dolaylı runtime | sklearn tarafından gerektiği ölçüde |
| python-dotenv | `.env` değerlerini process environment'a yükler | `settings.py`, `vector_settings.py` | Runtime | Yerel env yükleme için evet |
| pytest | 55 parametrik/unit test case'i | `tests/*`, test extra | Geliştirme | Runtime için hayır; doğrulama için evet |
| argparse | Mongo ana CLI ve search CLI argümanları | `main.py`, `search_vector_experiment.py` | Stdlib runtime | İlgili CLI'lar için evet |
| csv | Similarity, cluster ve audit tabular artifact'ları | `vector_experiment.py`, `cluster_article_vectors.py` | Stdlib runtime | Raporlar için evet |
| uuid5 | WOS UID'den deterministik Qdrant UUID point ID | `qdrant_vector_store.py` | Stdlib runtime | Qdrant load için evet |
| Mermaid | Yalnız bu audit belgesindeki diyagram markup'ı; runtime kodu değildir | `PROJECT_DATA_FLOW.md` | Dokümantasyon | Hayır |

## Özellikle bulunmayanlar

| Teknoloji/dosya | Sonuç |
|---|---|
| pandas | **[DOĞRULANDI]** Dependency veya import yok. CSV stdlib ile yazılıyor. |
| PyTorch | **[DOĞRULANDI]** Dependency/import yok ve aktif venv paket listesinde yok. Inference ONNX Runtime/FastEmbed. |
| `sentence-transformers` Python paketi | **[DOĞRULANDI]** Doğrudan dependency/import yok; ifade model repository kimliğinin parçası. |
| ruff / mypy / bandit | **[DOĞRULANDI]** `pyproject.toml` config/dependency yok; denetimde çalıştırılmadı. |
| requirements dosyası | **[DOĞRULANDI]** Yok; dependency kaynağı `pyproject.toml`. |
| lock dosyası | **[DOĞRULANDI]** Yok. Reproducibility riski. |
| Dockerfile | **[DOĞRULANDI]** Yok; upstream images kullanılıyor. |
| migration | **[DOĞRULANDI]** Repository'de migration dosyası yok. Redash ilk schema `create_db` ile manuel kuruluyor. |
| scripts klasörü/downloader | **[DOĞRULANDI]** Yok. Ham WOS dosyasını indiren kod yok. |

## Zorunluluk sınırları

`pyproject.toml` üç ayrı kapsam tanımlar:

- Ana bağımlılıklar: `ijson`, `pymongo`, `python-dotenv`.
- `vector`: FastEmbed, qdrant-client ve Python <3.9 için tokenizers constraint.
- `cluster`: matplotlib, qdrant-client, scikit-learn.
- `test`: pytest.

**[DOĞRULANDI]** Yalnız mevcut Qdrant vektörlerini cluster etmek FastEmbed
gerektirmez. Yeni query embedding'i, load veya similarity raporu `vector`
extra'sını gerektirir. Mongo/Redash akışı cluster/vector extra'sını gerektirmez.

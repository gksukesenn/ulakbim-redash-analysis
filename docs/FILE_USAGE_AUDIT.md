# Dosya kullanım denetimi

## Sınıflar

- A: aktif ve zorunlu
- B: aktif, geliştirme/test amaçlı
- C: generated report/artifact
- D: eski/yan deney
- E: duplicate/alternatif
- F: hiçbir yerden çağrılmayan
- G: amaç dışı olma ihtimali
- H: kullanımı doğrulanamayan
- I: silinmemesi gereken veri/konfigürasyon
- J: secret/local-only

“Aktif” bir CLI, import zinciri, test, README operasyonu veya Compose servisiyle
kanıtlanan dosyadır. Self-contained fakat belgelenmemiş modül “aktif” sayılmaz.

## Repository kökü ve altyapı

| Dosya yolu | Görevi | Kim tarafından çağrılıyor | Girdi | Çıktı | Aktif mi? | Kanıt |
|---|---|---|---|---|---|---|
| `README.md` | Kurulum, Mongo/Redash, vector deney ve komut rehberi | İnsan/operasyon | Repository yapısı | Talimat | Evet | Komutlar ve dosya linkleri; ana README |
| `pyproject.toml` | Paket/dependency/test config | pip, pytest, setuptools | TOML | Kurulu paket/test config | Evet | `[project]`, extras, pytest config |
| `.env.example` | Mongo, Redash, Qdrant değişken adı/örneği | İnsan; dotenv için şablon | Placeholder config | Yerel `.env` şablonu | Evet | README setup; iki settings modülü |
| `.env` | Gerçek yerel secret/config | python-dotenv, Compose | Secret/local ayarlar | Runtime config | Evet/local | `.gitignore`; değerleri audit'e alınmadı |
| `.gitignore` | Secret/raw/cache dışlama | Git | Pattern'ler | Tracking filtresi | Evet | `.env`, raw, cache pattern'leri |
| `docker-compose.yml` | MongoDB + Redash/Postgres/Redis stack | Docker Compose/README | env + named volumes | 8 servis | Evet | `README.md:166-190`; config doğrulandı |
| `docker-compose.vector-experiment.yml` | Qdrant service/volume | Docker Compose/README | image + volume | Qdrant service | Evet | `README.md:321-325`; canlı container |
| `data/raw/ulakbim_ubyt_wos_records.json` | 744 MB WOS kaynak snapshot'ı | `iter_publications` çağıran akışlar | JSON | 16.101 raw kayıt stream'i | Evet/local | `main.py:20-22`, selection `DATA_FILE` |
| `.venv/` | Yerel Python environment | İnsan/pip/python | Paketler | Interpreter/runtime | Evet/local | README kurulum; Git ignore |
| `src/ulakbim_redash_analysis.egg-info/*` | Editable install metadata | setuptools/pip üretir | pyproject/package | Generated metadata | Hayır/runtime kaynak değil | `*.egg-info` Git ignore; 5 dosya |
| `.pytest_cache/*` | pytest cache | pytest üretir | Test koşuları | Cache | Hayır | Cache marker; uygulama import etmez |
| `**/__pycache__/*.pyc` | Python bytecode cache | Interpreter üretir | `.py` | Cache | Hayır | `__pycache__` Git ignore |

Requirements, lock, Dockerfile, scripts ve migration dosyası bulunmamıştır.

## Domain ve infrastructure

| Dosya yolu | Görevi | Kim tarafından çağrılıyor | Girdi | Çıktı | Aktif mi? | Kanıt |
|---|---|---|---|---|---|---|
| `domain/publication.py` | Normalize yayın domain modeli | mapper, import, vector, test | Alan değerleri | `Publication` | Evet | Çoklu import; mapper testleri |
| `domain/vector_experiment.py` | Experiment/vector/search DTO'ları | vector app, Qdrant, cluster, test | Publication/vector/payload | Dataclass nesneleri | Evet | İlgili modül importları |
| `domain/__init__.py` | Paket marker | Python import sistemi | — | Paket | Evet | Package discovery |
| `infrastructure/json_reader.py` | ijson streaming adapter | import ve inspection/selection use case'leri | Raw JSON path | dict iterator | Evet | 8 application importu |
| `infrastructure/publication_mapper.py` | Raw WOS → Publication normalizer | import, validation, selection, tests | Raw dict | Publication | Evet | `map_publication` çağrıları; 26 mapper test case'i |
| `infrastructure/settings.py` | Mongo env config | `main._create_repository` | environment | MongoDBSettings | Evet | `main.py:17,122`; settings testleri |
| `infrastructure/mongodb_repository.py` | PyMongo adapter/index/upsert/count | `main.py` | Publication batch | Mongo writes/count | Evet | Main composition root |
| `infrastructure/vector_settings.py` | Qdrant/model/dimension env config | vector runtime, cluster | environment | VectorExperimentSettings | Evet | `create_vector_services`, cluster main |
| `infrastructure/local_embedding.py` | FastEmbed ONNX adapter | vector runtime | Text list | float vectors | Evet | `vector_experiment_runtime.py:3,14` |
| `infrastructure/qdrant_vector_store.py` | Qdrant create/upsert/search/scroll adapter | vector runtime, cluster | vectors/query | point/search/article DTO | Evet | Load/search/report/cluster zinciri |
| `infrastructure/__init__.py` | Paket marker | Python import sistemi | — | Paket | Evet | Package discovery |

## Application ve entry pointler

| Dosya yolu | Görevi | Kim tarafından çağrılıyor | Girdi | Çıktı | Aktif mi? | Kanıt |
|---|---|---|---|---|---|---|
| `main.py` | `inspect/validate/import/count` CLI composition root | `python -m ulakbim_analysis.main` | CLI/env/JSON/Mongo | Konsol/Mongo | Evet | README ve CLI test |
| `application/import_publications.py` | Streaming batch import use case | `main._run_import`, tests | Raw iterator/repository | ImportResult + writes | Evet | Main import; 11 test case'i |
| `application/publication_repository.py` | Mongo-independent Protocol/result | import use case, Mongo adapter, tests | Publication list | Write counters | Evet | Hem application hem infrastructure import eder |
| `application/inspect_dataset.py` | İlk kayıt shape | main inspect | JSON | Konsol | Evet | `main.py:10-12,163-164` |
| `application/validate_mapping.py` | İlk N mapper alan kontrolü | main validate ve kendi `__main__` | JSON | Konsol | Evet | README iki komut; main import |
| `application/analyze_all_abstracts.py` | Tüm raw abstract istatistiği | kendi `__main__`, tests | JSON | Konsol/result | Evet | README ve test |
| `application/inspect_abstracts.py` | İlk 1.000 abstract ham shape/uzunluk tanısı | Yalnız kendi `__main__` | JSON | Konsol | Sınırlı/H | `if __name__`; README hızlı kontrol metni başka modülü kullanır |
| `application/inspect_field_shapes.py` | Alan tip dağılımı helper'ı | Referans yok | JSON + explicit function call | Konsol | Hayır | `__main__` yok; rg import/call yok |
| `application/inspect_analysis_fields.py` | İlk kayıtta analiz alan örnekleri | Referans yok | JSON + explicit function call | Konsol | Hayır | `__main__` yok; rg import/call yok |
| `application/inspect_open_access.py` | OA anahtarlarını recursive arama | Referans yok | JSON + explicit function call | Konsol | Hayır | `__main__` yok; rg import/call yok |
| `application/vector_experiment_selection.py` | 24 sabit UID seçim use case'i | select/load/search/report | JSON | ExperimentArticle list | Evet | Dört application importu + test |
| `application/select_vector_experiment.py` | Seçimi salt okunur listeleyen CLI | kendi `__main__` | JSON | Konsol | Evet | README komutu |
| `application/vector_experiment.py` | Embedding text/payload/load/search/CSV use case'leri | load/search/report/tests | Articles + ports | VectorPoint/search/report | Evet | Dört module importu + 6 test case'i |
| `application/vector_experiment_runtime.py` | FastEmbed/Qdrant composition helper | load/search/report | env | embedder/store | Evet | Üç module importu |
| `application/load_vector_experiment.py` | 24 embed + destructive collection load CLI | kendi `__main__`, run | JSON/model/Qdrant | 24 Qdrant point | Evet/yazıcı | README ve run import |
| `application/search_vector_experiment.py` | UID/text query CLI | kendi `__main__` | JSON/model/Qdrant | Konsol top-N | Evet | README iki örnek |
| `application/report_vector_experiment.py` | 24×top-5 similarity MD/CSV | kendi `__main__`, run | JSON/model/Qdrant | 2 report | Evet/yan deney | README ve run import |
| `application/run_vector_experiment.py` | Load + report convenience CLI | kendi `__main__` | JSON/model/Qdrant | Collection + 2 report | Evet | README alternatif komut |
| `application/cluster_article_vectors.py` | Qdrant scroll, PCA, KMeans, 3 report | kendi `__main__`, tests | Qdrant | CSV/MD/PNG | Evet | 3 test; mevcut artifacts |
| `application/__init__.py`, `src/ulakbim_analysis/__init__.py` | Paket marker | Python import sistemi | — | Paket | Evet | Package discovery |

## Testler

| Dosya | Kapsam | Aktif kanıt | Sınıf |
|---|---|---|---|
| `tests/conftest.py` | Raw WOS fixture | pytest fixture discovery | B |
| `tests/test_cli.py` | argparse komutları/validation | 2/2 geçti | B |
| `tests/test_settings.py` | Mongo settings | 5/5 geçti | B |
| `tests/test_publication_mapper.py` | Bütün mapper normalizasyonları | 26/26 geçti | B |
| `tests/test_import_publications.py` | Batch/limit/error/idempotency fake repository | 11/11 geçti | B |
| `tests/test_analyze_all_abstracts.py` | Abstract istatistiği/error limiti | 2/2 geçti | B |
| `tests/test_vector_experiment.py` | Text, eligibility, payload, fake search, CSV, selection | 6/6 geçti | B |
| `tests/test_cluster_article_vectors.py` | PCA/KMeans ve report writer | 3/3 geçti | B |

Toplam pytest collection: 55 case. Gerçek MongoDB/Qdrant entegrasyon testi yoktur.

## Dokümantasyon, Redash ve raporlar

| Dosya yolu | Görevi | Kim tarafından çağrılıyor | Girdi | Çıktı | Aktif mi? | Kanıt |
|---|---|---|---|---|---|---|
| `docs/ARCHITECTURE.md` | Mongo/Redash mimari özeti | README linki | Kod tasarımı | Doküman | Evet | `README.md:56` |
| `docs/PROJECT_STUDY_GUIDE.md` | Ayrıntılı eski çalışma rehberi | İnsan | Mongo/Redash kodu | Doküman | Evet ama drift var | 39 test ifadesi güncel 55 değil; vector/kümeleme eksik |
| `docs/redash_queries/README.md` | Yedi query ve grafik/dashboard manuel kurulum | README/insan | Query JSON | Redash talimatı | Evet | `README.md:424-445` |
| `docs/redash_queries/01_total_unique_publications.json` | Publication count aggregation | Redash'te manuel paste | publications | count | Evet | Query README bölüm 1 |
| `docs/redash_queries/02_top_10_publishers.json` | Publisher top 10 | Aynı | publications | rows | Evet | Query README bölüm 2 |
| `docs/redash_queries/03_top_10_journals.json` | Journal top 10 | Aynı | publications | rows | Evet | Query README bölüm 3 |
| `docs/redash_queries/04_top_10_institutions.json` | Institution unwind/top 10 | Aynı | publications | rows | Evet | Query README bölüm 4 |
| `docs/redash_queries/05_top_10_subjects.json` | Subject unwind/top 10 | Aynı | publications | rows | Evet | Query README bölüm 5 |
| `docs/redash_queries/06_publications_by_year.json` | Year distribution | Aynı | publications | rows | Evet | Query README bölüm 6 |
| `docs/redash_queries/07_gold_oa_journal_distribution.json` | Gold OA distribution | Aynı | publications | rows | Evet | Query README bölüm 7 |
| `docs/images/dashboard-overview.png` | Dashboard kanıt görseli | README/docs | Manuel screenshot | PNG | Evet/artifact | README yayımlanabilir dashboard iddiası |
| `docs/images/dashboard-analyses.png` | Analiz görünümü | README/docs | Manuel screenshot | PNG | Evet/artifact | Dokümantasyon asset'i |
| `docs/images/docker-services.png` | Service görünümü | README/docs | Manuel screenshot | PNG | Evet/artifact | Dokümantasyon asset'i |
| `reports/article_clusters_pca.png` | PCA scatter | cluster CLI üretir | Qdrant | PNG | Generated | `PLOT_PATH`, `write_pca_plot` |
| `reports/article_cluster_assignments.csv` | Cluster/PCA atamaları | cluster CLI üretir | Qdrant | CSV | Generated | `CSV_PATH`, `write_assignments_csv` |
| `reports/article_cluster_summary.md` | Cluster istatistiği/listesi | cluster CLI üretir | Qdrant/settings | Markdown | Generated | `REPORT_PATH`, `write_summary` |
| `reports/vector_similarity_experiment.md` | Önceki cosine deney özeti | report/run CLI | JSON/model/Qdrant | Markdown | Generated/yan deney | README + report module |
| `reports/vector_similarity_results.csv` | 120 cosine çift + boş manual alanlar | report/run CLI | JSON/model/Qdrant | CSV | Generated/yan deney | Writer columns; hiçbir reader yok |
| `reports/audit_selected_articles.csv` | Bu audit'te raw selection + canlı point eşlemesi | Audit talebi | Raw/Qdrant salt okunur | CSV | Generated audit | 24 satır; DB yazısı yok |

## Cleanup adayları

| Dosya | Sınıf | Neden | Aktif referans | Silinirse risk | Öneri |
|---|---|---|---|---|---|
| `**/__pycache__/`, `*.pyc` | C | Bytecode cache | Yok | Düşük; yeniden oluşur | Git dışına almayı değerlendir |
| `.pytest_cache/` | C | Test cache | Yok | Düşük; test geçmişi kaybolur | Git dışına almayı değerlendir |
| `src/*.egg-info/` | C | Editable install metadata | pip üretir | Düşük; reinstall gerekir | Git dışına almayı değerlendir |
| `reports/vector_similarity_experiment.md` | C,D | Önceki cosine deney artifact'ı | README; writer | Bulgular kaybolur | Archive klasörüne taşımayı değerlendir |
| `reports/vector_similarity_results.csv` | C,D | Manuel review için üretildi; alanlar boş; cluster kullanmaz | README; yalnız writer | 120 mevcut skor ve review şablonu kaybolur | Archive klasörüne taşımayı değerlendir |
| `inspect_field_shapes.py` | F | Entry point/import/test yok | Yok | Eski keşif aracı kaybolabilir | Manuel inceleme gerekli |
| `inspect_analysis_fields.py` | F | Entry point/import/test yok | Yok | Eski keşif aracı kaybolabilir | Manuel inceleme gerekli |
| `inspect_open_access.py` | F | Entry point/import/test yok | Yok | OA shape araştırması kaybolabilir | Manuel inceleme gerekli |
| `inspect_abstracts.py` | H | Self-entry var; README/test referansı yok | Yalnız kendi `__main__` | Ham abstract teşhis aracı kaybolur | Manuel inceleme gerekli |
| `PROJECT_STUDY_GUIDE.md` | H | Aktif doküman fakat test sayısı stale ve yeni vector alanı eksik | İnsan | Tarihsel bilgi/kanıt kaybolur | Koru |
| 3 dashboard PNG | C,I | Manuel kanıt asset'ları; tekrar üretim otomatik değil | Doküman | Görsel kanıt kaybolur | Koru |
| `data/raw/*.json` | I | Tek gerçek kaynak snapshot; Git ignored | Tüm veri akışları | Yeniden edinme yolu kodda yok, kritik veri kaybı | Koru |
| `.env` | J,I | Secret/local runtime config | dotenv/Compose | Servis erişimi bozulur; secret sızabilir | Koru |
| `.env.example` | I | Secret olmayan şablon | README | Kurulum zorlaşır | Koru |
| iki Compose + named volumes | I | İki korunan çalışma alanının servis/persistence tanımı | README/operasyon | Mongo/Redash/Qdrant erişimi veya veri kaybı | Koru |

## Sayısal sınıflandırma notu

Denetim başlangıcında `.git`, `.venv`, `__pycache__` ve `.pytest_cache` hariç 71
mantıksal dosya incelendi; ayrıca 53 cache dosyası gözlendi. Beş mevcut report
artifact'ı ve üç dashboard screenshot generated/manuel artifact'tır. Beş
`egg-info` dosyası build artifact'ıdır. Kullanılmayan kesin aday sayısı üçtür;
`inspect_abstracts.py` ayrı “kullanımı doğrulanamayan” kategorisindedir.

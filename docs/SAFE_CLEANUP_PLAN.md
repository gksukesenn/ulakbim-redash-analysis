# Güvenli cleanup planı

Bu belge yalnız öneridir. Hiçbir cleanup uygulanmamıştır.

## Ön koşullar

1. Dirty çalışma ağacındaki bütün kullanıcı değişiklikleri incelenmeli ve güvenli
   bir commit/backup alınmalıdır.
2. MongoDB, Redash PostgreSQL ve Qdrant named volume'larının adları ve yedekleme
   yöntemi doğrulanmalıdır. `docker compose down -v` kullanılmamalıdır.
3. Başlangıç snapshot'ı alınmalıdır: branch, `git status`, raw dosya boyut/hash,
   Mongo collection list/count/index, Qdrant collection/count/schema.
4. `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest
   -p no:cacheprovider` başarıyla geçmelidir.
5. Archive/silme listesi kullanıcı tarafından dosya bazında onaylanmalıdır.

## Aşama 1 — cache/build artifact adayları

| Aday | Neden | Risk | Öneri | Geri alma |
|---|---|---|---|---|
| `**/__pycache__/`, `*.pyc` | Yeniden üretilebilir bytecode | Çok düşük; ilk import yavaşlayabilir | Git dışına almayı değerlendir | Python importu yeniden üretir |
| `.pytest_cache/` | Test cache | Çok düşük; pytest süre/history bilgisi sıfırlanır | Git dışına almayı değerlendir | pytest yeniden üretir |
| `src/ulakbim_redash_analysis.egg-info/` | Editable install build metadata | Düşük; environment metadata geçici eksilir | Git dışına almayı değerlendir | `pip install -e ...` yeniden üretir |
| Matplotlib cache | Workspace içinde tespit edilmedi; audit komutu `/tmp` kullandı | Bilinmeyen dış cache'e dokunma riski | Manuel inceleme gerekli | Cache yeniden üretilebilir; path önce kesinleştirilmeli |

Bu adaylar veri tabanı veya source değildir; yine de bu turda silinmemiştir.

## Aşama 2 — önce archive kararı gereken deney artifact'ları

| Aday | Neden | Risk | Öneri | Geri alma |
|---|---|---|---|---|
| `reports/vector_similarity_experiment.md` | Kümeleme için bağımlılık değil, önceki cosine deneyi | Örnek skorlar ve deney açıklaması kaybolur; yeniden üretim model/Qdrant sürümüne bağlı değişebilir | Archive klasörüne taşımayı değerlendir | Git/backup veya aynı report komutu; birebir sonuç garanti değil |
| `reports/vector_similarity_results.csv` | 120 pair ve boş manuel etiket alanı; aktif reader yok | İnsan review şablonu/skor snapshot'ı kaybolur | Archive klasörüne taşımayı değerlendir | Git/backup; report komutu yeniden üretir |

Üretici application modülleri (`report_vector_experiment.py`, search/load/run)
README'de aktif belgelenmiştir; artifact archive kararı üretici kodun silinmesini
otomatik olarak gerektirmez.

## Aşama 3 — manuel kod incelemesi gereken modüller

| Aday | Kanıt | Risk | Öneri |
|---|---|---|---|
| `application/inspect_field_shapes.py` | Import, test, README, `__main__` yok | Ham schema keşif kabiliyeti kaybolur | Manuel inceleme gerekli |
| `application/inspect_analysis_fields.py` | Aynı | Örnek alan shape çıktısı kaybolur | Manuel inceleme gerekli |
| `application/inspect_open_access.py` | Aynı | OA alan keşif aracı kaybolur | Manuel inceleme gerekli |
| `application/inspect_abstracts.py` | Yalnız self-entry; README/test yok | Abstract teşhis aracı kaybolur | Manuel inceleme gerekli |

Onay sonrası tercih sırası: önce archive/commit geçmişi, sonra test, en son silme.
Bu dosyalara ilişkin “silme adayı” kararı yalnız referans taramasına dayanarak
otomatik verilmemelidir.

## Kesinlikle silinmemesi gerekenler

- `data/raw/ulakbim_ubyt_wos_records.json`: tek kaynak snapshot; downloader yok.
- `.env`: local-only secret config; Git'e alınmamalı, içeriği paylaşılmamalı.
- `.env.example`, `.gitignore`, `pyproject.toml`, `README.md`.
- `docker-compose.yml`, `docker-compose.vector-experiment.yml`.
- `mongodb_data`, `redash_postgres_data`, `qdrant_experiment_data` named volumes.
- Canlı `ulakbim_article_similarity_experiment` collection ve 24 point.
- `src/ulakbim_analysis/domain`, aktif application ve infrastructure adaptörleri.
- `tests/`, `docs/redash_queries/`, dashboard ekran görüntüleri.
- Güncel cluster artifact'ları, kullanıcı sonuç olarak korumak istediği sürece.

## Her cleanup dalgasından sonra doğrulama

1. `git diff --check` ve `git status --short`.
2. 55 pytest case'inin tamamı.
3. Bütün Python dosyalarında AST parse/import kontrolü.
4. Yedi Redash query JSON'unda JSON parse.
5. İki Compose dosyasında `docker compose ... config -q`.
6. MongoDB document count ve index listesi; yalnız servis kullanıcı tarafından
   güvenli biçimde başlatılmışsa.
7. Qdrant point count=24, size=384, distance=Cosine.
8. Raw dosya hash/size karşılaştırması.
9. Beklenmeyen yeni dosya ve report farkı kontrolü.

## Geri alma yöntemi

- Tracked dosya: onaylı commit'ten dosya bazında geri al; broad `git reset
  --hard` kullanma.
- Untracked kullanıcı dosyası: silmeden önce workspace dışı doğrulanmış backup
  veya archive manifesti oluştur.
- Cache: ilgili araç yeniden üretir.
- Generated report: üretici komut ve input provenance'ı saklanmışsa yeniden
  üret; aynı package/model sürümü sabit değilse birebir byte eşitliği bekleme.
- Mongo/Qdrant/volume: yalnız doğrulanmış backup restore prosedürü; cleanup
  kapsamında doğrudan silme yok.

## Onay kapısı

Henüz hiçbir dosya silinmedi, taşınmadı veya yeniden adlandırılmadı. Cleanup
işlemi kullanıcı onayı bekliyor.

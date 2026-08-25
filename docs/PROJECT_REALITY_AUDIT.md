# Proje gerçeklik denetimi

Denetim tarihi: 4 Ağustos 2026. Bu belge yalnız repository kodu, mevcut ham
dosya, generated raporlar ve salt okunur servis sorgularına dayanır. `.env`
değerleri rapora alınmamıştır.

Etiketler:

- **[DOĞRULANDI]** Kod veya mevcut veri üzerinden kesin doğrulandı.
- **[ÇIKARIM]** Birden fazla işarete dayanan, fakat doğrudan kod kuralı olmayan yorum.
- **[DOĞRULANAMADI]** Repository ve erişilebilir çalışma zamanı kesin cevap vermedi.

## Yönetici özeti

- **[DOĞRULANDI]** Projenin iki gerçek çalışma alanı vardır: 16.101 ham WOS
  kaydını streaming okuyup 16.083 benzersiz UID üzerinden MongoDB/Redash ile
  analiz etmek; aynı ham dosyadan sabit 24 UID seçip hazır modelle Qdrant
  benzerlik ve Python tarafı PCA/KMeans deneyi yapmak. Kanıt:
  `json_reader.py:7-22`, `main.py:20-22,132-143`,
  `vector_experiment_selection.py:9-76`, `vector_experiment.py:71-103`.
- **[DOĞRULANDI]** Ham dosya `data/raw/ulakbim_ubyt_wos_records.json`, boyutu
  744.550.524 byte ve mevcut içerikte 16.101 kayıt/16.083 benzersiz UID vardır.
  18 kayıt yinelenen UID'dir. Bu denetimde dosya streaming taranmıştır.
- **[DOĞRULANDI]** Canlı Qdrant collection'ı
  `ulakbim_article_similarity_experiment`, 24 point, 384 boyut ve `Cosine`
  metriğindedir. Başlangıç point count: 24.
- **[DOĞRULANAMADI]** MongoDB ve Redash container'ları denetim başlangıcında
  durmuş olduğu için canlı collection listesi, belge sayısı ve dashboard
  metadata'sı sorgulanamadı. Kod varsayılan olarak `ulakbim_analysis` veritabanı
  ve `publications` collection'ını kullanır (`settings.py:8-20`). README daha
  önce 16.083 belge raporlar (`README.md:409,418`), fakat bu canlı ölçüm değildir.
- **[DOĞRULANDI]** 55 test geçti; testler gerçek MongoDB/Qdrant entegrasyonu
  yerine fake nesneler kullanır. Qdrant store ve canlı MongoDB için entegrasyon
  testi yoktur (`tests/test_import_publications.py:14-42`,
  `tests/test_vector_experiment.py:24-42`).

## Projenin gerçek amacı ve tamamlanan işler

### A. MongoDB + Redash

**[DOĞRULANDI]** `ijson` ile büyük JSON belleğe bütünüyle alınmadan okunur,
ham kayıt `Publication` modeline normalize edilir, UID bazlı unordered bulk
upsert ile MongoDB'ye yazılır. Yedi MongoDB aggregation sorgusu ve bunların
Redash'te elle kurulmasına ilişkin talimatlar repository'dedir. Dashboard'un
canlı PostgreSQL metadata export'u repository'de yoktur; üç ekran görüntüsü
vardır. Kanıt: `json_reader.py`, `publication_mapper.py`,
`mongodb_repository.py`, `docs/redash_queries/*.json`,
`docs/redash_queries/README.md`, `docs/images/*.png`.

### B. Embedding + Qdrant + kümeleme

**[DOĞRULANDI]** 24 sabit UID ham dosyadan alınır; başlık ve abstract bir metin
şablonunda birleştirilir; FastEmbed'in hazır ONNX modeli vektör üretir; Qdrant
collection yeniden oluşturulup vektörler yazılabilir. Ayrı modüller cosine
benzerlik raporu ve mevcut vektörlerden PCA/KMeans raporu üretir. Yeni model
eğitimi, fine-tuning, train/test ayrımı veya ground truth yoktur. Kanıt:
`vector_experiment_selection.py`, `local_embedding.py`, `vector_experiment.py`,
`report_vector_experiment.py`, `cluster_article_vectors.py`.

## Veri seti ve MongoDB + Redash gerçek veri akışı

### Kesin cevaplar

1. **[DOĞRULANDI] Kaynak:** `data/raw/ulakbim_ubyt_wos_records.json`;
   `main.py:20-22` ve diğer analiz modüllerinin `DATA_FILE` sabitleri.
2. **[DOĞRULANDI] JSON path:** `item.Data.Records.records.REC.item`;
   `json_reader.py:7,17-21`. Üst seviye array öğesi `item`, ardından `Data`,
   `Records`, `records`, `REC` array öğesi `item` olarak izlenir.
3. **[DOĞRULANDI] Streaming:** Evet. Dosya binary açılır; `ijson.items` bir
   generator üzerinden kayıtları tek tek `yield` eder (`json_reader.py:10-22`).
4. **[DOĞRULANDI] Okuyucu:** `ijson>=3.3,<4` (`pyproject.toml`).
5. **[DOĞRULANDI] Hamdan alınan alanlar:** UID; item/source title; publisher
   isimleri; `pubyear`; `journal_oas_gold`; abstract paragrafları; address
   organization'ları; subjects; doctypes; languages; keywords
   (`publication_mapper.py:69-378`). `dynamic_data` modele alınmaz.
6. **[DOĞRULANDI] Normalizasyon:** dict/list varyantları normalize edilir;
   metinler `strip` edilir ve boşsa `None` olur; listelerde tekrarlar ilk sıra
   korunarak kaldırılır; publisher'da `unified_name`, `full_name`,
   `display_name` önceliği vardır; kurumda `pref=Y` tercih edilir; abstract
   paragrafları boşlukla birleştirilir; yıl `int`, Y/N Gold OA `bool` olur;
   10.000 karakter üzeri abstract şüpheli işaretlenir.
7. **[DOĞRULANDI] Domain alanları:** `uid`, `title`, `journal`, `publisher`,
   `publication_year`, `journal_gold_open_access`, `abstract`,
   `abstract_length`, `abstract_is_suspicious`, `institutions`, `subjects`,
   `document_types`, `languages`, `keywords` (`publication.py:8-32`).
8. **[DOĞRULANDI] MongoDB belgesi:** `dataclasses.asdict(Publication)` sonucu
   aynı alanlarla `$set` edilir (`mongodb_repository.py:60-68`).
9. **[DOĞRULANDI] Collection:** varsayılan `publications`; ortamda
   `MONGODB_COLLECTION` ile değişebilir (`settings.py:8-20,42-49`). Canlı değer
   servis durmuş olduğu için **[DOĞRULANAMADI]**.
10. **[DOĞRULANDI] Index:** uygulama `uid_unique` adlı ascending, unique UID
    indexini `import` öncesi oluşturur (`main.py:132-141`,
    `mongodb_repository.py:42-49`). Canlı index durumu **[DOĞRULANAMADI]**.
11. **[DOĞRULANDI] Redash bağlantısı:** Compose ağı içinde hostname `mongodb`;
    data source formu manuel oluşturulur. Repository'de otomatik provisioning
    kodu yoktur (`README.md:213-237`, `docker-compose.yml:15-36`).
12. **[DOĞRULANDI] Redash sorguları:** Yedi JSON aggregation ve ayrıntılı
    görselleştirme rehberi vardır. Canlı dashboard tanımı/export'u yoktur.
13. **[DOĞRULANDI] Yazma entry point'i:** `python -m ulakbim_analysis.main
    import`; `_run_import` → `import_publications` → `upsert_publications`.
14. **[DOĞRULANDI] Salt okunur entry point'ler:** `main inspect`, `main
    validate`, `main count` (DB count), `validate_mapping`,
    `analyze_all_abstracts`, `inspect_abstracts`, `select_vector_experiment`,
    `search_vector_experiment` ve `cluster_article_vectors`ın Qdrant okuma kısmı.
    Sonuncusu repository rapor dosyalarını yeniden yazar; veri tabanını yazmaz.

### Gerçek çağrı zinciri

```text
data/raw/ulakbim_ubyt_wos_records.json
  ↓ iter_publications / infrastructure/json_reader.py
ijson.items(..., "item.Data.Records.records.REC.item")
  ↓ map_publication / infrastructure/publication_mapper.py
Publication / domain/publication.py
  ↓ import_publications + import_publication_records / application/import_publications.py
PublicationRepository Protocol / application/publication_repository.py
  ↓ MongoDBRepository.upsert_publications / infrastructure/mongodb_repository.py
MongoDB ulakbim_analysis.publications
  ↓ docs/redash_queries/01..07 JSON aggregationları
Redash MongoDB data source
  ↓ docs/redash_queries/README.md içindeki manuel görselleştirme ayarları
Grafik / dashboard (canlı metadata repository'de yok)
```

## 24 makalenin gerçek seçim yöntemi

### On üç sorunun cevabı

1. **[DOĞRULANDI]** Kaynak, MongoDB değil aynı ham JSON dosyasıdır:
   `vector_experiment_selection.py:9,73-76`.
2. **[DOĞRULANDI]** Evet, `SELECTIONS` içinde elle kodlanmış 24 WOS UID vardır
   (`vector_experiment_selection.py:15-40`).
3. **[DOĞRULANDI]** Çalışma zamanında anahtar kelime araması yoktur.
4. **[DOĞRULANDI]** Subject/category ile filtre yoktur.
5. **[DOĞRULANDI]** Başlık ile filtre yoktur.
6. **[DOĞRULANDI]** Abstract konu seçimi için aranmaz; yalnız mevcut olması ve
   şüpheli olmaması eligibility kontrolüdür (`:54-57`).
7. **[DOĞRULANDI]** İlk N seçimi değildir; tüm stream hedef UID'ler bulunana
   kadar taranır (`:47-68`).
8. **[DOĞRULANDI]** Üç grupta sekizer UID kodda açıktır (`:11-40`).
9. **[DOĞRULANAMADI]** UID listesini ilk oluşturan konu sorguları/anahtar
   kelimeler repository'de yoktur. `selection_reason` kısa insan açıklamasıdır;
   yürütülen sorgu değildir.
10. **[DOĞRULANDI]** Aynı ham içerik için seçim deterministiktir ve sonuç UID'ye
    göre sıralanır (`:70`).
11. **[DOĞRULANDI]** Aynı 24 UID dosyada mevcut ve eligible kaldığı sürece aynı
    24 makale seçilir.
12. **[DOĞRULANDI]** Random seçim yoktur; seed yoktur.
13. **[DOĞRULANDI]** Tam UID/başlık listesi aşağıdadır ve
    `reports/audit_selected_articles.csv` içinde point ID'leriyle verilmiştir.
14. **[DOĞRULANDI]** Abstract eksik veya 10.000 karakterden uzun/şüpheliyse
    kayıt atlanır (`:54-57`). Mevcut 24 kaydın tamamı abstract sahibidir ve
    şüpheli değildir (ham dosyanın salt okunur taraması).
15. **[DOĞRULANDI]** `remaining_uids` seti bir UID ilk görüldüğünde kaldırır;
    dolayısıyla duplicate seçilmez (`:47,51-56`). Mevcut seçili UID'lerin ham
    dosyada duplicate'i yoktur. Not: İlk duplicate kopya uygunsuzsa UID yine
    setten kaldırıldığı için sonraki uygun kopya denenmez.

### Tam liste

| Grup | UID | Tam başlık |
|---|---|---|
| different_mental_health | WOS:001129852800002 | The effect of occupational therapy on anxiety, depression, and psychological well-being in older adults: a single-blind randomized-controlled study |
| same_topic_perovskite_solar_cells | WOS:001131514500001 | Magnetic-biased chiral molecules enabling highly oriented photovoltaic perovskites |
| same_topic_perovskite_solar_cells | WOS:001140573400001 | Acetate-based ionic liquid engineering for efficient and stable CsPbI<sub>2</sub>Br perovskite solar cells with an unprecedented fill factor over 83% |
| related_energy_technologies | WOS:001140575800001 | Understanding the role of water in the lyotropic liquid crystalline mesophase of high-performance flexible supercapacitor electrolytes using a rheological approach |
| different_mental_health | WOS:001142171500001 | Biological Markers in Newly Diagnosed Generalized Anxiety Disorder Patients: 8-OHdG, S100B and Oxidative Stress |
| related_energy_technologies | WOS:001143201300001 | Incorporating Gadolinium Oxide (Gd<sub>2</sub>O<sub>3</sub>) as a Rare Earth Metal Oxide in Carbon Nanofiber Skeleton for Supercapacitor Application |
| same_topic_perovskite_solar_cells | WOS:001143809700001 | Constructing Charge Bridge Path for High-Performance Tin Perovskite Photovoltaics |
| related_energy_technologies | WOS:001144493500001 | Crystallinity tuning of LCNO/graphene nanocomposite cathode for high-performance lithium-ion batteries |
| different_mental_health | WOS:001148762500002 | Exploring adult attachment and anxiety: the role of intolerance of uncertainty and social support |
| related_energy_technologies | WOS:001149960200001 | Applications of artificial neural network based battery management systems: A literature review |
| different_mental_health | WOS:001154920600001 | Effect of online health training/counseling and progressive muscle relaxation exercise on postpartum depression and maternal attachment: A randomized controlled trial |
| different_mental_health | WOS:001157189800001 | Predictors, moderators and mediators of psychological therapies for perinatal depression in low- and middle-income countries: a systematic review |
| different_mental_health | WOS:001157724100001 | Depression and life satisfaction after Kahramanmaraş earthquakes: The serial mediation roles of life meaning and coping with earthquake stress |
| same_topic_perovskite_solar_cells | WOS:001158980200001 | Synergistic Effects of Energy Level Alignment and Trap Passivation via 3,4-Dihydroxyphenethylamine Hydrochloride for Efficient and Air-Stable Perovskite Solar Cells |
| related_energy_technologies | WOS:001163332000001 | Gellan gum/PEDOT:PSS gel electrolyte and application on quasi-solid dye sensitized solar cells |
| different_mental_health | WOS:001163480800004 | Effects of a Mindfulness-Based Stress Reduction Program on Stress, Depression, and Psychological Well-being in Patients With Cancer |
| related_energy_technologies | WOS:001165771600001 | The effect of outer container geometry on the thermal management of lithium-ion batteries with a combination of phase change material and metal foam |
| same_topic_perovskite_solar_cells | WOS:001167231700001 | Incorporation Mechanism of Potassium in FAPbI<sub>3</sub> Perovskite Solar Cell Materials |
| related_energy_technologies | WOS:001168109200001 | High-performance Na-ion full-cells with P2-type Na<sub>0.67</sub>Mn<sub>0.5-x</sub>Ni<sub>x</sub>Fe<sub>0.43</sub>Al<sub>0.07</sub>O<sub>2</sub> cathodes: Cost analysis for stationary battery storage systems |
| related_energy_technologies | WOS:001168628400001 | Simulation and forecasting of power by energy harvesting method in photovoltaic panels using artificial neural network |
| same_topic_perovskite_solar_cells | WOS:001173733800001 | Ion-Migration Inhibitor for Spiro-OMeTAD/Perovskite Contact toward Stable Perovskite Solar Cells |
| same_topic_perovskite_solar_cells | WOS:001178378200001 | Molecular modification of spiro[fluorene-9,9′-xanthene]-based dopant-free hole transporting materials for perovskite solar cells |
| different_mental_health | WOS:001182798400001 | Multitask Learning for Mental Health: Depression, Anxiety, Stress (DAS) Using Wearables |
| same_topic_perovskite_solar_cells | WOS:001191208900001 | Molecularly Engineered Multifunctional Bridging Layer Derived from Dithiafulavene Capped Spiroxanthene for Stable and Efficient Perovskite Solar Cells |

## Embedding süreci

1. **[DOĞRULANDI] Model:**
   `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`;
   `vector_settings.py:10-13`.
2. **[DOĞRULANDI] Yükleme:** `FastEmbedModel.__init__`, FastEmbed
   `TextEmbedding(model_name=model_name)` (`local_embedding.py:4-18`).
3. **[DOĞRULANDI] Cache ayarı:** proje `cache_dir` vermez. Kurulu FastEmbed
   imzasında default `None`'dır. **[DOĞRULANAMADI]** Modelin bu makinede hangi
   fiziksel cache dizininden ilk kez edinildiği repository kodundan belirlenmez.
4. **[DOĞRULANDI] Gerçek metin:** yalnız title+abstract:
   `Başlık: {title}\nAbstract: {abstract}` (`vector_experiment.py:50-53`).
   Keywords, subjects ve journal modele verilmez.
5. **[DOĞRULANDI] Eksik abstract:** seçim ve `create_vector_points` aşamalarında
   atlanır; `build_embedding_text` tek başına çağrılsaydı `Abstract yok` yazar,
   fakat yükleme akışında bu dala uygun olmayan kayıt ulaşmaz (`:71-82`).
6. **[DOĞRULANDI] Preprocessing:** mapper metinlerin baş/son boşluğunu kırpar,
   abstract paragraflarını tek boşlukla birleştirir. Lowercase yapılmaz; HTML
   etiketleri temizlenmez; tokenization parametresi proje kodunda verilmez.
7. **[DOĞRULANDI] Boyut:** ayar ve canlı collection 384'tür.
8. **[DOĞRULANDI] Normalizasyon:** proje kodu açık normalize parametresi vermez.
   Kurulu FastEmbed 0.4.2'nin `OnnxTextEmbedding._post_process_onnx_output`
   implementasyonu çıktıyı L2 normalize eder. Bu, repository'ye pinlenen exact
   patch sürüm garantisi değildir (`fastembed>=0.3,<0.6`).
9. **[DOĞRULANDI] Batch:** 24 metin tek Python listesi olarak `embed` çağrısına
   verilir; proje `batch_size` vermez. Kurulu FastEmbed default'u 256'dır.
10. **[DOĞRULANDI] Encode parametreleri:** proje yalnız model adını ve metin
    listesini verir; `batch_size`, `parallel`, provider, device veya CUDA
    parametresi vermez (`local_embedding.py:7-18`).
11. **[DOĞRULANDI]** Eğitim ve fine-tuning yoktur.
12. **[DOĞRULANDI]** Train/test süreci yoktur; testler kod birim testleridir.
13. **[DOĞRULANDI]** Sonuç `VectorPoint` domain nesnesine, sonra
    `QdrantVectorStore.upsert` içindeki `PointStruct`'a gider.
14. **[DOĞRULANDI] Payload:** `uid`, `title`, `journal`, `publication_year`,
    `subjects`, `experiment_group`, `selection_reason`, ilk 240 karakter
    `abstract_preview` (`vector_experiment.py:56-68`). Tam abstract saklanmaz.

### Makale seçim algoritması

1. Ham JSON `iter_publications` ile streaming okunur.
2. Raw `UID`, `SELECTIONS` sabit sözlüğünün kalan UID setinde değilse geçilir.
3. Eşleşen kayıt `map_publication` ile normalize edilir ve UID kalan setten çıkarılır.
4. Abstract yoksa veya 10.000 karakterden uzunsa kayıt seçilmez.
5. Sözlükteki group/reason ile `ExperimentArticle` oluşturulur.
6. Tüm hedefler görüldüğünde stream durur; sonuç UID'ye göre sıralanır.

### Embedding üretim algoritması

1. Eligible `ExperimentArticle` nesneleri tekrar abstract kontrolünden geçer.
2. Her biri `Başlık: ...\nAbstract: ...` metnine dönüştürülür.
3. Bütün metin listesi hazır FastEmbed `TextEmbedding.embed` metoduna verilir.
4. Kurulu adaptör float array'leri Python listelerine çevirir.
5. Makale sayısı ile vektör sayısı eşleşmezse hata verilir.
6. Her sonuç metadata ile `VectorPoint` olur.

### Qdrant'a yazma algoritması

1. `load_vector_experiment.main` ham dosyadan seçili makaleleri yükler.
2. `create_vector_services` hazır modeli ve Qdrant store'u oluşturur.
3. `load_articles_to_store` önce `recreate_collection` çağırır.
4. Varsa collection tamamen silinir; 384/Cosine şemasıyla yeniden yaratılır.
5. Her UID `uuid5(NAMESPACE_URL, uid)` ile deterministik point ID'ye çevrilir.
6. Vektör ve payload `PointStruct` listesiyle `wait=True` upsert edilir.

## Qdrant'ın gerçek rolü

| Soru | Yanıt ve kanıt |
|---|---|
| Collection | **[DOĞRULANDI]** `ulakbim_article_similarity_experiment`; `vector_settings.py:8-13`, canlı API. |
| Vector size | **[DOĞRULANDI]** 384; ayar ve canlı API. |
| Distance | **[DOĞRULANDI]** Cosine; `qdrant_vector_store.py:27-38`, canlı API. |
| Rol | **[DOĞRULANDI]** Vektör/payload saklama, scroll ve nearest-neighbor query. Model çalıştırmaz. |
| Clustering | **[DOĞRULANDI]** Qdrant clustering yapmaz. KMeans Python/scikit-learn tarafındadır. |
| Yazma komutu | **[DOĞRULANDI]** `python -m ulakbim_analysis.application.load_vector_experiment`; birleşik alternatif `run_vector_experiment`. |
| Tekrar çalıştırma | **[DOĞRULANDI]** Duplicate yaratmaz; fakat güvenli bir salt upsert de değildir. Collection önce silinip yeniden oluşturulur. Hata halinde geçici veri kaybı riski vardır. |
| Point ID | **[DOĞRULANDI]** URL namespace UUIDv5 + WOS UID; aynı UID aynı ID'yi verir (`:43-49`). |
| Payload yeterliliği | **[DOĞRULANDI]** UID ve başlık makaleyi seçili veri içinde tanımlar; tam abstract yoktur. Kaynak snapshot/version bilgisi yoktur. |
| Deney/production | **[DOĞRULANDI]** Adlar, README ve group metadata bunu deneysel collection olarak tanımlar. Production SLA/şema migration kodu yoktur. |
| Count | **[DOĞRULANDI]** Analiz öncesi 24; analiz sonrası ölçüm sonuç bölümünde. |

## Kümeleme ve grafik üretimi

1. **[DOĞRULANDI]** `QdrantVectorStore.read_all_articles` scroll ile payload ve
   vektörü çeker (`qdrant_vector_store.py:85-120`).
2. **[DOĞRULANDI]** Pagination vardır: limit 100, `offset` `None` olana kadar.
3. **[DOĞRULANDI]** Canlıda 24 vektör alınır.
4. **[DOĞRULANAMADI]** Proje scroll'a explicit order/sort vermez. Mevcut API
   yanıtı UUID sırasındadır; bunun kalıcı sözleşme olduğu proje kodundan çıkmaz.
5. **[DOĞRULANDI]** KMeans 384 boyutlu özgün vektör listesinde çalışır.
6. **[DOĞRULANDI]** Kod PCA koordinatlarını önce hesaplar, fakat KMeans'e PCA
   sonucu değil özgün `vectors` verilir (`cluster_article_vectors.py:47-51`).
7. **[DOĞRULANDI]** `k=3`, deney isteği ve üç ön seçim grubuyla uyumludur.
   Algoritmik model seçimi/elbow/silhouette yapılmamıştır.
8. **[DOĞRULANDI]** `cluster_count` fonksiyon parametresidir, default 3; CLI
   argümanı değildir. Grafik/rapor metninde 3 sabittir (`:26-29,129,154`).
9. **[DOĞRULANDI]** `random_state=42`; `n_init=10` (`:50`).
10. **[DOĞRULANDI]** sklearn KMeans küme merkezlerine kareli Öklid uzaklığı
    mantığını kullanır; Qdrant cosine yalnız search metriğidir.
11. **[DOĞRULANDI]** Kümeleme kodu KMeans öncesi normalize etmez. Mevcut
    vektörlerin üretildiği kurulu FastEmbed sürümü L2-normalize çıktı üretir;
    Qdrant'tan başka kaynaktan gelen vektör için bu garanti edilmez.
12. **[ÇIKARIM]** Birim normlu vektörlerde cosine benzerliği ile kareli Öklid
    uzaklığı monotonic ilişkilidir (`||x-y||²=2-2cos(x,y)`); klasik KMeans
    merkezlerinin her iterasyonda küreye yeniden normalize edilmemesi nedeniyle
    spherical/cosine KMeans ile tamamen aynı algoritma değildir.
13. **[DOĞRULANDI]** PCA yalnız koordinat/plot ve açıklanan varyans için
    kullanılır; KMeans girdisi değildir.
14. **[DOĞRULANDI]** `PCA(n_components=2).explained_variance_ratio_` raporlanır;
    mevcut sonuç PC1 %23,86, PC2 %13,98, toplam %37,85'tir.
15. **[DOĞRULANDI]** `model.inertia_` raporlanır; mevcut değer 7,615551'dir.
16. **[DOĞRULANDI]** Kümelerin algoritmik adları yalnız `0`, `1`, `2`'dir.
17. **[DOĞRULANDI]** “Batarya/enerji”, “psikoloji”, “perovskit” ifadeleri KMeans
    tarafından üretilmez. Kodun ön seçim group/reason metinlerinden ve raporu
    okuyan insan yorumundan gelir. Cluster summary bu adları yazmaz.
18. **[DOĞRULANDI]** Küme başına tam liste
    `reports/article_cluster_summary.md:16-47` içindedir; her kümede sekiz kayıt.
19. **[DOĞRULANDI]** Grafik annotation başlıkları 34 karakteri aşınca 33
    karakter+ellipsis olur; okunabilirliği sınırlamak için `_short_title`
    kullanılır (`cluster_article_vectors.py:89-90,121-128`).
20. **[DOĞRULANDI]** PNG'nin görsel incelemesinde özellikle sol alt perovskit
    noktalarında annotation çakışmaları vardır. Kod collision avoidance veya
    `adjustText` kullanmaz.

### Kümeleme algoritması

1. Ayarlar yüklenir, Qdrant bağlantısı salt okunur doğrulanır.
2. Scroll ile mevcut vector/payload'ların tamamı okunur.
3. Boş veya farklı boyuttaki vektörler reddedilir.
4. Özgün vektörlere iki bileşenli PCA fit edilir ve koordinatlar hesaplanır.
5. Aynı özgün vektörlere KMeans (`k=3`, seed 42, `n_init=10`) fit/predict edilir.
6. UID, title, cluster ve PCA koordinatı `ClusterAssignment` olur.
7. Explained variance ratio ve inertia alınır.
8. CSV, PNG ve Markdown generated artifact'ları yazılır.

### Grafik üretim algoritması

1. Her assignment'ın `pca_x`/`pca_y` koordinatı alınır.
2. Cluster numaraları sıralanır; her cluster'ın üyeleri ayrılır.
3. Üç renk döngüsüyle scatter noktaları ve `Küme N (n=...)` legend'i çizilir.
4. Her noktaya `CN · kısa başlık` annotation'ı 5 piksel offset ile eklenir.
5. Başlık, eksenler, grid ve legend eklenir; `tight_layout` uygulanır.
6. 15×10 inch figure, 180 DPI PNG olarak kaydedilir.

## Üretilen raporların kaynağı

| Dosya | Üreten komut/modül | Giriş | Amaç ve durum |
|---|---|---|---|
| `reports/article_clusters_pca.png` | `python -m ulakbim_analysis.application.cluster_article_vectors` | Canlı Qdrant 24 vektör | Küme/PCA görseli; güncel kümeleme amacına hizmet eden generated artifact; manuel işlem yok; Qdrant aynıysa yeniden üretilebilir. Sonuç belgelenecekse Git'e dahil edilebilir, zorunlu runtime dosyası değildir. |
| `reports/article_cluster_assignments.csv` | aynı | Qdrant vector/payload | 24 atama ve PCA koordinatı; güncel generated artifact; aktif kod bunu yalnız yazar, geri okumaz. |
| `reports/article_cluster_summary.md` | aynı | assignment, ayar/model, canlı distance | İstatistik ve cluster listesi; güncel generated artifact; aktif kod bunu yalnız yazar. |
| `reports/vector_similarity_experiment.md` | `python -m ulakbim_analysis.application.report_vector_experiment` veya `run_vector_experiment` | Ham 24 makalenin yeniden embedding query'si + Qdrant search | Önceki benzerlik deneyi; ana kümeleme için gerekli değil; generated artifact; yeniden üretim model çalıştırır ve raporu yazar ama Qdrant'a yazmaz. |
| `reports/vector_similarity_results.csv` | aynı | 24×ilk 5 cosine sonuç | İnsan incelemesi için boş `manual_label` ve `reviewer_note` sütunları açıkça üretilir (`vector_experiment.py:14-24`, `report_vector_experiment.py:43-53,177-183`). Mevcut 120 satırda iki sütun da tamamen boştur. Kümeleme kodu/testleri okumaz; yalnız similarity rapor kodu üretir. Eski/yan deney artifact'ıdır. |

## Entry point envanteri

| Komut | Modül | Amaç | Okur | Yazar | Tekrar çalıştırma |
|---|---|---|---|---|---|
| `python -m ulakbim_analysis.main inspect` | `main.py` | İlk ham kayıt yapısı | JSON | Hayır | Güvenli |
| `... main validate --limit N` | `main.py` | Mapper doğrulama | JSON | Hayır | Güvenli |
| `... main import [--limit]` | `main.py` | MongoDB import | JSON/MongoDB | MongoDB + index | UID upsert idempotent; veri değiştirebilir |
| `... main count` | `main.py` | Belge count | MongoDB | Hayır | Güvenli, servis gerekir |
| `python -m ...validate_mapping` | `validate_mapping.py` | Varsayılan 1.000 mapper kontrolü | JSON | Hayır | Güvenli |
| `python -m ...analyze_all_abstracts` | `analyze_all_abstracts.py` | Tüm raw abstract istatistiği | JSON | Hayır | Güvenli, tam scan |
| `python -m ...inspect_abstracts` | `inspect_abstracts.py` | İlk 1.000 abstract shape/uzunluk | JSON | Hayır | Güvenli; README'de yok |
| `python -m ...select_vector_experiment` | `select_vector_experiment.py` | 24 seçimi yazdırır | JSON | Hayır | Güvenli |
| `python -m ...load_vector_experiment` | `load_vector_experiment.py` | Embedding ve Qdrant load | JSON/model/Qdrant | Collection'ı siler/yeniden yazar | Destructive recreate; otomatik çalıştırılmamalı |
| `python -m ...search_vector_experiment --uid/--text` | `search_vector_experiment.py` | Benzerlik arama | JSON/model/Qdrant | Hayır | DB açısından güvenli; query embedding üretir |
| `python -m ...report_vector_experiment` | `report_vector_experiment.py` | Similarity raporları | JSON/model/Qdrant | 2 report | Qdrant salt okunur; artifact overwrite |
| `python -m ...run_vector_experiment` | `run_vector_experiment.py` | Load+report birleşik | JSON/model/Qdrant | Qdrant + report | Destructive recreate |
| `MPLCONFIGDIR=/tmp/... python -m ...cluster_article_vectors` | `cluster_article_vectors.py` | PCA/KMeans | Qdrant | 3 report | Qdrant salt okunur; artifact overwrite |
| `python -m pytest` | pytest | 55 test case | Kod/fixture | temp/cache olabilir | `-p no:cacheprovider`, `PYTHONDONTWRITEBYTECODE=1` ile çalışma ağacı güvenli |
| `docker compose ...` | Compose | MongoDB/Redash veya Qdrant stack | YAML/env | Container/volume durumu | `config -q` güvenli; `up/import/create_db/down -v` aynı değildir |

`inspect_field_shapes.py`, `inspect_analysis_fields.py` ve
`inspect_open_access.py` içinde `__main__` bloğu yoktur; public fonksiyonları
başka modül/test tarafından import edilmez.

## Clean architecture değerlendirmesi

### Uyan noktalar

- **[DOĞRULANDI]** Domain dataclass'ları JSON, MongoDB ve Qdrant SDK'sı import
  etmez (`domain/*.py`).
- **[DOĞRULANDI]** Mongo import use case'i `PublicationRepository` Protocol'üne
  bağlıdır ve fake repository ile test edilir.
- **[DOĞRULANDI]** Embedding/search çekirdeği `Embedder` ve `VectorStore`
  Protocol'leriyle test edilebilir (`vector_experiment.py:27-47`).
- **[DOĞRULANDI]** JSON, MongoDB, embedding ve Qdrant somut adaptörleri
  `infrastructure` altındadır.
- **[DOĞRULANDI]** `main.py` Mongo CLI composition root görevi görür.

### Uymayan veya zayıf noktalar

- **[DOĞRULANDI]** Bazı application modülleri doğrudan infrastructure
  implementasyonlarını import eder: `import_publications.py` reader/mapper'ı,
  selection reader/mapper'ı, clustering doğrudan Qdrant store/settings'i,
  runtime doğrudan FastEmbed/Qdrant'ı bilir. Dependency inversion tam değildir.
- **[DOĞRULANDI]** `MongoDBRepository` infrastructure'dan application içindeki
  `RepositoryWriteResult`'ı import eder; bu izin verilen inward dependency olsa
  da DTO'nun application'da olması adapterı use case'e bağlar.
- **[DOĞRULANDI]** CLI'lar tek composition root'ta toplanmamıştır; application
  modülleri aynı zamanda `if __name__` entry point ve dosya yazıcıdır.
- **[DOĞRULANDI]** `VectorStore` Protocol'ü yalnız write/search metodlarını
  kapsar; clustering'in read interface'i yoktur ve concrete store'a bağlıdır.
- **[ÇIKARIM]** Yapı “clean architecture esintili katmanlama”dır; eksiksiz clean
  architecture değildir.

## Doğrulanmış bilgiler, doğrulanamayanlar ve yorumlar

### Doğrulanmış

- Raw: 16.101 kayıt, 16.083 benzersiz UID, 18 duplicate-extra, 0 UNKNOWN,
  mapper scan'de 0 hata.
- Seçili 24 UID ham dosyada birer kez var; tamamında normal abstract var.
- Canlı Qdrant 24/384/Cosine ve payload alanları kodla eşleşiyor.
- Similarity CSV 120 satır; manuel alanların hiçbiri doldurulmamış.
- PCA/KMeans artifact'ları 24 satır ve 8/8/8 dağılım raporluyor.
- PostgreSQL makale deposu değildir; Compose'ta Redash'in
  `REDASH_DATABASE_URL` hedefidir. Redis Redash queue/koordinasyonudur.

### Koddan doğrulanamadı

- 24 UID'nin ilk kez hangi sorgu, anahtar kelime veya insan incelemesiyle
  belirlendiği.
- Canlı MongoDB collection listesi/count/indexleri; servis durmuştu.
- Canlı Redash dashboard'un repository JSON'larıyla birebir aynı olup olmadığı.
- Modelin ilk indirilme zamanı ve bu makinedeki fiziksel cache kaynağı.
- Qdrant scroll sırasının kalıcı ordering garantisi.
- Dashboard ekran görüntülerinin tam üretim zamanı ve canlı sürümle eşitliği.

### Çıkarımlar

- `SELECTIONS` group/reason metinleri ve sekizer dağılım, kontrollü bir benzerlik
  deneyi tasarlandığını gösterir; fakat seçim hazırlama prosedürü kod değildir.
- Similarity raporları güncel kümeleme için bağımlılık değil, önceki/yan deneydir.
- `PROJECT_STUDY_GUIDE.md` ayrıntılı fakat 39 test ifadesi güncel 55 testten
  eskidir; vektör/kümeleme akışını kapsamaması doküman drift'idir.

## Riskler ve teknik borçlar

1. Qdrant load collection'ı önce siler; atomic migration/rollback yoktur.
2. `fastembed>=0.3,<0.6` geniş aralığı normalize/cache/runtime davranışını patch
   sürümler arasında sabitlemez; lock dosyası yoktur.
3. Mongo/Redash ve Qdrant için gerçek entegrasyon testleri yoktur.
4. Clustering CLI `k` argümanı sunmaz; plot/report metni 3'e sabittir, fonksiyon
   parametresi farklı verilirse doküman yanlış olur.
5. KMeans açık normalize yapmaz; provenance/model sürümü Qdrant payload'ında
   point bazında saklanmaz.
6. PCA yalnız %37,85 varyansı gösterir; 2B görsel ayrım tam 384B yapının tamamı
   değildir.
7. PNG etiket collision çözümü yoktur.
8. Raw snapshot hash/version ve Qdrant load timestamp'i saklanmaz.
9. README clustering komutunu belgelemiyor; vector extra ile cluster extra ayrı,
   ancak birlikte gereken kullanım açık değil.
10. Çalışma ağacı audit öncesinde zaten dirty ve vektör/kümeleme dosyalarının
    çoğu Git tarafından izlenmiyordu; yanlış cleanup veri/kod kaybı yaratabilir.

## Cleanup adayları ve korunacaklar

Ayrıntı `docs/FILE_USAGE_AUDIT.md` ve `docs/SAFE_CLEANUP_PLAN.md` içindedir.

- **Kesin koru:** `data/raw` (local-only), `.env` (secret/local-only), iki
  Compose dosyası, source/domain/application/infrastructure aktif akışları,
  tests, Redash query JSON/README, named volume'lar ve canlı Qdrant collection.
- **Generated/cache:** `__pycache__`, `.pytest_cache`, `*.egg-info`; onayla ve
  Git dışında tutarak temizlenebilir, uygulama verisi değildir.
- **Archive değerlendirmesi:** iki similarity report artifact'ı, ana kümeleme
  hedefinden bağımsız eski/yan deney çıktılarıdır; üretici kod hâlâ aktif ve
  README'de belgeli olduğundan doğrudan silinmemelidir.
- **Manuel inceleme:** çağrılmayan üç eski inspection modülü ve README'de
  belgelenmeyen `inspect_abstracts.py`.

## Güvenli doğrulama sonucu

- Branch: `main`.
- Başlangıç git durumu: kullanıcıya ait çok sayıda modified/untracked dosya;
  denetim bunları değiştirmedi.
- Çalışan proje servisi: yalnız Qdrant; MongoDB/Redash exited.
- Test: 55/55 geçti.
- AST parse: 40 Python dosyası geçti.
- JSON: 7/7 Redash query dosyası geçti.
- Compose: 2/2 config `-q` doğrulaması geçti.
- Qdrant point count: analiz öncesi **24**, analiz sonrası **24**; size ve
  distance sırasıyla 384/Cosine kaldı.
- MongoDB document count: analiz öncesi **[DOĞRULANAMADI]**, analiz sonrası
  **[DOĞRULANAMADI]**; container iki ölçümde de `Exited (0)` durumundaydı ve
  kullanıcı talimatı gereği başlatılmadı.
- Bitiş Docker durumu başlangıçla aynıdır: yalnız Qdrant sağlıklı çalışıyor;
  MongoDB ve bütün Redash stack durmuş durumda.
- Git durumuna yalnız bu audit için istenen beş Markdown ve bir CSV eklendi;
  başlangıçta mevcut application/config/report değişiklikleri korunup
  düzenlenmedi.
- Lint/type/security araçları pyproject'te tanımlı değildir; ruff, mypy, bandit
  çalıştırılmadı.

## Sonraki güvenli adımlar

1. Bu audit'i kullanıcıyla onaylayın; cleanup başlamasın.
2. MongoDB/Redash'in kullanıcı tarafından normal operasyonla başlatıldığı ayrı
   bir bakım penceresinde yalnız count/index/dashboard doğrulaması yapın.
3. Dirty çalışma ağacındaki kullanıcı değişikliklerini commit/stash stratejisiyle
   güvenceye almadan hiçbir cleanup yapmayın.
4. Cache temizliği yapılacaksa önce test ve veri count snapshot'ı alın.
5. Eski deney raporlarını silmek yerine önce archive kararı verin.

Henüz hiçbir dosya silinmedi, taşınmadı veya yeniden adlandırılmadı. Cleanup
işlemi kullanıcı onayı bekliyor.

# Vektör benzerliği öğrenme deneyi

## Amaç

Bu deney 24 kontrollü makaleyi embedding vektörlerine dönüştürür, Qdrant'ta saklar ve cosine similarity sıralamasını insan gözüyle incelemeye açar. Skor bir doğruluk yüzdesi değildir.

## Model seçimi

Model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Model cümle ve paragrafları 384 boyutlu yoğun vektörlere dönüştürür; 50 dili destekler ve Apache-2.0 lisanslıdır. FastEmbed'in ONNX çalıştırıcısı CPU üzerinde yerel çalışır; API anahtarı veya ücretli servis kullanmaz. Küçük deney için yaklaşık 220 MB'lık model, daha büyük çok dilli modellere göre daha kolay tekrarlanabilir.

Embedding girdisi açıkça `Başlık: ...\nAbstract: ...` şablonudur. Abstract'sız ve şüpheli abstract'lı kayıtlar yüklenmez.

## Qdrant kavramları

- **Collection:** Aynı vektör şemasını kullanan point kümesi; bu deneyin ayrı tablosu gibi düşünülebilir.
- **Point:** Bir makaleyi temsil eden kayıt; kimlik, vector ve payload içerir.
- **Vector:** Metnin anlamını sayılarla temsil eden 384 elemanlı embedding.
- **Payload:** UID, başlık, dergi, yıl, subjects, deney grubu ve kısa abstract önizlemesi gibi okunabilir metadata.
- **Vector dimension:** Her vector içindeki sayı adedi; burada 384.
- **Distance metric:** Qdrant sıralamada cosine benzerliğini kullanır; vektörlerin yönlerinin ne kadar benzer olduğunu karşılaştırır.

## Seçilen makale grupları

### `different_mental_health`

- `WOS:001129852800002` — The effect of occupational therapy on anxiety, depression, and psychological well-being in older adults: a single-blind randomized-controlled study — seçim nedeni: Yaşlılarda anksiyete/depresyon
- `WOS:001142171500001` — Biological Markers in Newly Diagnosed Generalized Anxiety Disorder Patients: 8-OHdG, S100B and Oxidative Stress — seçim nedeni: Anksiyete biyobelirteçleri
- `WOS:001148762500002` — Exploring adult attachment and anxiety: the role of intolerance of uncertainty and social support — seçim nedeni: Bağlanma ve anksiyete
- `WOS:001154920600001` — Effect of online health training/counseling and progressive muscle relaxation exercise on postpartum depression and maternal attachment: A randomized controlled trial — seçim nedeni: Doğum sonrası depresyon
- `WOS:001157189800001` — Predictors, moderators and mediators of psychological therapies for perinatal depression in low- and middle-income countries: a systematic review — seçim nedeni: Perinatal depresyon terapisi
- `WOS:001157724100001` — Depression and life satisfaction after Kahramanmaraş earthquakes: The serial mediation roles of life meaning and coping with earthquake stress — seçim nedeni: Deprem sonrası depresyon
- `WOS:001163480800004` — Effects of a Mindfulness-Based Stress Reduction Program on Stress, Depression, and Psychological Well-being in Patients With Cancer — seçim nedeni: Kanserde stres ve depresyon
- `WOS:001182798400001` — Multitask Learning for Mental Health: Depression, Anxiety, Stress (DAS) Using Wearables — seçim nedeni: Giyilebilirlerle ruh sağlığı

### `related_energy_technologies`

- `WOS:001140575800001` — Understanding the role of water in the lyotropic liquid crystalline mesophase of high-performance flexible supercapacitor electrolytes using a rheological approach — seçim nedeni: Süperkapasitör elektroliti
- `WOS:001143201300001` — Incorporating Gadolinium Oxide (Gd<sub>2</sub>O<sub>3</sub>) as a Rare Earth Metal Oxide in Carbon Nanofiber Skeleton for Supercapacitor Application — seçim nedeni: Süperkapasitör elektrodu
- `WOS:001144493500001` — Crystallinity tuning of LCNO/graphene nanocomposite cathode for high-performance lithium-ion batteries — seçim nedeni: Lityum iyon katot
- `WOS:001149960200001` — Applications of artificial neural network based battery management systems: A literature review — seçim nedeni: Batarya yönetim sistemleri
- `WOS:001163332000001` — Gellan gum/PEDOT:PSS gel electrolyte and application on quasi-solid dye sensitized solar cells — seçim nedeni: Boya duyarlı güneş hücresi
- `WOS:001165771600001` — The effect of outer container geometry on the thermal management of lithium-ion batteries with a combination of phase change material and metal foam — seçim nedeni: Batarya termal yönetimi
- `WOS:001168109200001` — High-performance Na-ion full-cells with P2-type Na<sub>0.67</sub>Mn<sub>0.5-x</sub>Ni<sub>x</sub>Fe<sub>0.43</sub>Al<sub>0.07</sub>O<sub>2</sub> cathodes: Cost analysis for stationary battery storage systems — seçim nedeni: Sodyum iyon batarya
- `WOS:001168628400001` — Simulation and forecasting of power by energy harvesting method in photovoltaic panels using artificial neural network — seçim nedeni: Fotovoltaik güç tahmini

### `same_topic_perovskite_solar_cells`

- `WOS:001131514500001` — Magnetic-biased chiral molecules enabling highly oriented photovoltaic perovskites — seçim nedeni: Yönelimli perovskit
- `WOS:001140573400001` — Acetate-based ionic liquid engineering for efficient and stable CsPbI<sub>2</sub>Br perovskite solar cells with an unprecedented fill factor over 83% — seçim nedeni: Perovskit hücre kararlılığı
- `WOS:001143809700001` — Constructing Charge Bridge Path for High-Performance Tin Perovskite Photovoltaics — seçim nedeni: Kalay perovskit fotovoltaik
- `WOS:001158980200001` — Synergistic Effects of Energy Level Alignment and Trap Passivation via 3,4-Dihydroxyphenethylamine Hydrochloride for Efficient and Air-Stable Perovskite Solar Cells — seçim nedeni: Perovskit pasivasyonu
- `WOS:001167231700001` — Incorporation Mechanism of Potassium in FAPbI<sub>3</sub> Perovskite Solar Cell Materials — seçim nedeni: Perovskit malzeme katkılama
- `WOS:001173733800001` — Ion-Migration Inhibitor for Spiro-OMeTAD/Perovskite Contact toward Stable Perovskite Solar Cells — seçim nedeni: Perovskit temas kararlılığı
- `WOS:001178378200001` — Molecular modification of spiro[fluorene-9,9′-xanthene]-based dopant-free hole transporting materials for perovskite solar cells — seçim nedeni: Perovskit taşıma malzemesi
- `WOS:001191208900001` — Molecularly Engineered Multifunctional Bridging Layer Derived from Dithiafulavene Capped Spiroxanthene for Stable and Efficient Perovskite Solar Cells — seçim nedeni: Perovskit ara katmanı

## Örnek arama sonuçları

### `WOS:001140573400001` — Acetate-based ionic liquid engineering for efficient and stable CsPbI<sub>2</sub>Br perovskite solar cells with an unprecedented fill factor over 83%

1. `WOS:001158980200001` — 0.816264 — Synergistic Effects of Energy Level Alignment and Trap Passivation via 3,4-Dihydroxyphenethylamine Hydrochloride for Efficient and Air-Stable Perovskite Solar Cells — `same_topic_perovskite_solar_cells`
2. `WOS:001191208900001` — 0.777110 — Molecularly Engineered Multifunctional Bridging Layer Derived from Dithiafulavene Capped Spiroxanthene for Stable and Efficient Perovskite Solar Cells — `same_topic_perovskite_solar_cells`
3. `WOS:001167231700001` — 0.776720 — Incorporation Mechanism of Potassium in FAPbI<sub>3</sub> Perovskite Solar Cell Materials — `same_topic_perovskite_solar_cells`
4. `WOS:001173733800001` — 0.757365 — Ion-Migration Inhibitor for Spiro-OMeTAD/Perovskite Contact toward Stable Perovskite Solar Cells — `same_topic_perovskite_solar_cells`
5. `WOS:001178378200001` — 0.727099 — Molecular modification of spiro[fluorene-9,9′-xanthene]-based dopant-free hole transporting materials for perovskite solar cells — `same_topic_perovskite_solar_cells`

### `WOS:001163332000001` — Gellan gum/PEDOT:PSS gel electrolyte and application on quasi-solid dye sensitized solar cells

1. `WOS:001191208900001` — 0.654022 — Molecularly Engineered Multifunctional Bridging Layer Derived from Dithiafulavene Capped Spiroxanthene for Stable and Efficient Perovskite Solar Cells — `same_topic_perovskite_solar_cells`
2. `WOS:001140573400001` — 0.636101 — Acetate-based ionic liquid engineering for efficient and stable CsPbI<sub>2</sub>Br perovskite solar cells with an unprecedented fill factor over 83% — `same_topic_perovskite_solar_cells`
3. `WOS:001144493500001` — 0.631469 — Crystallinity tuning of LCNO/graphene nanocomposite cathode for high-performance lithium-ion batteries — `related_energy_technologies`
4. `WOS:001140575800001` — 0.631084 — Understanding the role of water in the lyotropic liquid crystalline mesophase of high-performance flexible supercapacitor electrolytes using a rheological approach — `related_energy_technologies`
5. `WOS:001173733800001` — 0.615967 — Ion-Migration Inhibitor for Spiro-OMeTAD/Perovskite Contact toward Stable Perovskite Solar Cells — `same_topic_perovskite_solar_cells`

### `WOS:001157724100001` — Depression and life satisfaction after Kahramanmaraş earthquakes: The serial mediation roles of life meaning and coping with earthquake stress

1. `WOS:001163480800004` — 0.505401 — Effects of a Mindfulness-Based Stress Reduction Program on Stress, Depression, and Psychological Well-being in Patients With Cancer — `different_mental_health`
2. `WOS:001129852800002` — 0.482473 — The effect of occupational therapy on anxiety, depression, and psychological well-being in older adults: a single-blind randomized-controlled study — `different_mental_health`
3. `WOS:001154920600001` — 0.458438 — Effect of online health training/counseling and progressive muscle relaxation exercise on postpartum depression and maternal attachment: A randomized controlled trial — `different_mental_health`
4. `WOS:001157189800001` — 0.455971 — Predictors, moderators and mediators of psychological therapies for perinatal depression in low- and middle-income countries: a systematic review — `different_mental_health`
5. `WOS:001148762500002` — 0.454983 — Exploring adult attachment and anxiety: the role of intolerance of uncertainty and social support — `different_mental_health`

## Gözlem adayları

- En yüksek karşılaştırma: `WOS:001173733800001` → `WOS:001178378200001`, skor 0.893280.
- Raporlanan en düşük ilk-5 karşılaştırması: `WOS:001157724100001` → `WOS:001148762500002`, skor 0.454983.
- Gruplar arası en yüksek sınır adayı: `WOS:001144493500001` → `WOS:001158980200001`, skor 0.667028. Bu çift özellikle `manual_label` ve `reviewer_note` alanlarında incelenmelidir.

## Neden evrensel bir eşik yok?

Cosine skorlarının ölçeği modele, metin şablonuna, dil ve konu dağılımına bağlıdır. Aynı skor bir veri setinde güçlü, başka bir veri setinde zayıf ilişki anlamına gelebilir. Bu nedenle otomatik etiket atanmadı; CSV'deki `manual_label` alanı insan incelemesine bırakıldı.

## 100 ve 1.000 kayda geçmeden önce

- Aynı, yakın ve farklı grup çiftlerini elle etiketleyip hata örüntülerini karşılaştırın.
- Başlık ve abstract katkısını ayrı deneylerle ölçün.
- 512 token model sınırında uzun abstract kesilmesinin etkisini inceleyin.
- Türkçe ve düşük temsil edilen diller için ayrıca örnek seçin.
- Model ve veri seçimini sabitleyip tekrarlanabilirliği doğrulayın.

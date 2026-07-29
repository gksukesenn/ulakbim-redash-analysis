# Redash sorguları ve görselleştirme ayarları

Bu klasördeki JSON dosyaları, Redash MongoDB sorgu editörüne doğrudan
yapıştırılacak sorgulardır. Dosyalar açıklama veya Markdown içermez. Bütün
sorgular `publications` collection'ını kullanır.

Redash'in MongoDB query runner'ı `$sort` aşamasında standart MongoDB
`{"alan": -1}` nesnesi yerine aşağıdaki listeli biçimi bekler:

```json
{
  "$sort": [
    {
      "name": "alan_adi",
      "direction": -1
    }
  ]
}
```

Bu nedenle repository'deki sorgularda sort aşamalarını standart MongoDB
shell biçimine çevirmeyin. `direction` için `-1` azalan, `1` artan sıralamadır.

## Sorguları Redash'te oluşturma

Her dosya için Redash'te **Create > Query** seçin, `ULAKBİM MongoDB` data
source'unu belirleyin, JSON içeriğini editöre yapıştırın ve **Execute** ile
çalıştırın. Sorguyu aşağıda belirtilen sorgu adıyla kaydedin. Ardından **New
Visualization** ile belirtilen görselleştirmeyi oluşturup dashboard'a ekleyin.

## 01 — Toplam benzersiz yayın

- Dosya: `01_total_unique_publications.json`
- Redash sorgu adı: `Toplam Benzersiz Yayın Sayısı`
- Amaç: `publications` collection'ındaki benzersiz MongoDB belge sayısını
  göstermek.
- Collection: `publications`
- Beklenen sonuç sütunları: `toplam_yayin`
- Görselleştirme türü: Counter
- Değer alanı: `toplam_yayin`
- Görselleştirme adı ve önerilen başlık: `Toplam Benzersiz Yayın`
- Özel ayarlar: Counter value column olarak `toplam_yayin` seçilir.
- Dashboard konumu: Üst bölümde geniş veya orta boy kart.

## 02 — İlk 10 yayıncı

- Dosya: `02_top_10_publishers.json`
- Redash sorgu adı: `En Fazla Yayına Sahip İlk 10 Yayıncı`
- Amaç: Boş olmayan yayıncılar arasında yayın sayısı en yüksek ilk 10 değeri
  göstermek.
- Collection: `publications`
- Beklenen sonuç sütunları: `yayinci`, `yayin_sayisi`
- Görselleştirme türü: Bar chart
- Eksenler: Y Column `yayinci`; X Columns `yayin_sayisi`
- Önerilen başlık: `En Fazla Yayına Sahip İlk 10 Yayıncı`
- Özel ayarlar: Horizontal Chart açık, Sort Values kapalı, Show Labels açık ve
  Data Labels açık olmalıdır. En yüksek değer yanlış tarafta görünürse Reverse
  Order ayarını kontrol edin.
- Dashboard konumu: Toplam kartının altında, dergi grafiğinin yanında yarım
  genişlik.

## 03 — İlk 10 dergi

- Dosya: `03_top_10_journals.json`
- Redash sorgu adı: `En Fazla Yayına Sahip İlk 10 Dergi`
- Amaç: Boş olmayan dergiler arasında yayın sayısı en yüksek ilk 10 değeri
  göstermek.
- Collection: `publications`
- Beklenen sonuç sütunları: `dergi`, `yayin_sayisi`
- Görselleştirme türü: Bar chart
- Eksenler: Y Column `dergi`; X Columns `yayin_sayisi`
- Önerilen başlık: `En Fazla Yayına Sahip İlk 10 Dergi`
- Özel ayarlar: Horizontal Chart açık, Sort Values kapalı, Show Labels açık ve
  Data Labels açık olmalıdır.
- Dashboard konumu: Yayıncı grafiğinin yanında yarım genişlik.

## 04 — İlk 10 kurum

- Dosya: `04_top_10_institutions.json`
- Redash sorgu adı: `En Fazla Yayına Sahip İlk 10 Kurum`
- Amaç: Kurum array'ini açarak en çok yayında adı geçen ilk 10 kurumu
  göstermek.
- Collection: `publications`
- Beklenen sonuç sütunları: `kurum`, `yayin_sayisi`
- Görselleştirme türü: Bar chart
- Eksenler: Y Column `kurum`; X Columns `yayin_sayisi`
- Önerilen başlık: `En Fazla Yayına Sahip İlk 10 Kurum`
- Özel ayarlar: Horizontal Chart açık, Sort Values kapalı ve Data Labels açık
  olmalıdır. `$unwind` nedeniyle aynı yayın birden fazla kuruma katkı
  sağlayabilir; kategori toplamları benzersiz yayın sayısını göstermek zorunda
  değildir.
- Dashboard konumu: Yayıncı ve dergi grafiklerinin altındaki satırda yarım
  genişlik.

## 05 — İlk 10 konu

- Dosya: `05_top_10_subjects.json`
- Redash sorgu adı: `En Fazla Yayına Sahip İlk 10 Konu`
- Amaç: Konu array'ini açarak en çok yayında yer alan ilk 10 konuyu göstermek.
- Collection: `publications`
- Beklenen sonuç sütunları: `konu`, `yayin_sayisi`
- Görselleştirme türü: Bar chart
- Eksenler: Y Column `konu`; X Columns `yayin_sayisi`
- Önerilen başlık: `En Fazla Yayına Sahip İlk 10 Konu`
- Özel ayarlar: Horizontal Chart açık, Sort Values kapalı ve Data Labels açık
  olmalıdır. `$unwind` nedeniyle aynı yayın birden fazla konuya katkı
  sağlayabilir; kategori toplamları benzersiz yayın sayısını göstermek zorunda
  değildir.
- Dashboard konumu: Kurum grafiğinin yanında yarım genişlik.

## 06 — Yıllara göre yayın dağılımı

- Dosya: `06_publications_by_year.json`
- Redash sorgu adı: `Yıllara Göre Yayın Dağılımı`
- Amaç: Yayınları yayın yılına göre saymak ve kronolojik dağılımı göstermek.
- Collection: `publications`
- Beklenen sonuç sütunları: `yil`, `yayin_sayisi`
- Görselleştirme türü: Line chart
- Eksenler: X Column `yil`; Y Columns `yayin_sayisi`
- Önerilen başlık: `Yıllara Göre Yayın Dağılımı`
- Özel ayarlar: X Axis Scale `Category` ve Data Labels açık olmalıdır. 2026
  verisi kısmi dönemi temsil ediyor olabilir; dashboard açıklamasında bu not
  korunmalıdır.
- Dashboard konumu: Alt bölümde Gold OA grafiğinin yanında geniş veya yarım
  genişlik.

## 07 — Gold Open Access dergi dağılımı

- Dosya: `07_gold_oa_journal_distribution.json`
- Redash sorgu adı: `Gold Open Access Dergi Dağılımı`
- Amaç: Yayınları kaynak derginin Gold Open Access durumuna göre gruplamak.
- Collection: `publications`
- Beklenen sonuç sütunları: `gold_oa_durumu`, `yayin_sayisi`
- Görselleştirme türü: Pie veya Donut chart
- Alanlar: X Column/kategori `gold_oa_durumu`; Y Columns/değer
  `yayin_sayisi`
- Önerilen başlık: `Gold Open Access Dergi Dağılımı`
- Özel ayarlar: Data Labels açık; `Gold OA Dergi` yeşil, `Gold OA Değil` gri
  olmalıdır. Bu değer genel makale Open Access statüsü değildir;
  `journal_oas_gold` ham alanından türetilerek `journal_gold_open_access`
  model alanında tutulan dergi Gold OA durumudur.
- Dashboard konumu: Alt bölümde yıl grafiğinin yanında yarım genişlik.

## Önerilen dashboard düzeni

Dashboard adı `ULAKBİM Bilimsel Yayın Analizleri` olmalıdır. Üstte toplam
counter kartı; devamında ikili satırlar hâlinde yayıncı/dergi, kurum/konu ve
yıl/Gold OA grafikleri önerilir. Widget'ları ekledikten sonra dashboard'u
**Publish** ile yayımlayın.

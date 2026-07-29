# Mimari

Proje, sorumlulukları sade biçimde ayıran üç katmandan oluşur:

- `domain`: Analizde kullanılan `Publication` iş modelini içerir. JSON,
  MongoDB veya terminal ayrıntılarını bilmez.
- `application`: Veri içe aktarma ve inceleme kullanım senaryolarını yönetir.
  İçe aktarma akışı yalnızca küçük bir repository sözleşmesine bağımlıdır.
- `infrastructure`: Büyük JSON dosyasını `ijson` ile streaming okur, ham
  kayıtları modele dönüştürür, ortam ayarlarını yükler ve MongoDB işlemlerini
  gerçekleştirir.

`main.py`, terminal komutlarını tanımlar ve somut altyapı bileşenlerini
application kullanım senaryolarına bağlar.

## Veri akışı

```text
Ham Web of Science JSON
  -> ijson streaming reader
  -> publication mapper
  -> Publication domain modeli
  -> import kullanım senaryosu
  -> MongoDB repository
  -> MongoDB
  -> Redash sorguları
  -> grafikler
  -> dashboard
```

Redash sorguları, grafikler ve yayımlanan dashboard MongoDB'nin devamındaki
analiz katmanıdır. Sorguların yeniden oluşturulabilir kopyaları
`docs/redash_queries/` altında tutulur. Domain ve application katmanları bu
görselleştirme altyapısına bağımlı değildir.

## Temel kararlar

- Ham JSON hiçbir zaman bütünüyle belleğe alınmaz veya değiştirilmez.
- MongoDB'ye yalnızca sadeleştirilmiş `Publication` belgeleri yazılır.
- UID unique index ve upsert birlikte kullanılarak tekrar çalıştırılabilirlik
  sağlanır.
- UID değeri `UNKNOWN` olan kayıtlar kalıcı depoya gönderilmez.
- `journal_gold_open_access`, genel makale Open Access durumu değil, Gold Open
  Access dergi bilgisidir.

# Doğrulanabilir Dijital Kura Sistemi

Bu proje, kamuya açık kura ve çekiliş süreçlerinde **hızlı**, **şeffaf**, **tekrar üretilebilir** ve **bağımsız olarak doğrulanabilir** bir yöntem sunmak için hazırlanmış basit bir Python prototipidir.

Temel fikir şudur:

- Katılımcı listesi önceden sabitlenir.
- Çekiliş zamanı önceden ilan edilir.
- O anda henüz kimsenin bilemeyeceği bir dış rastgelelik kaynağı kullanılır.
- Sonuçlar herkese açık kod ile üretilir.
- İsteyen herkes aynı liste + aynı zaman + aynı kod ile aynı sonucu tekrar elde eder.

Bu sayede “Bize güvenin” yaklaşımı yerine, **“Siz de kontrol edin”** yaklaşımı sağlanır.

---

## Amaç

Bu prototip özellikle şu tür süreçler için uygundur:

- sosyal konut kurası
- kamu çekilişleri
- belediye veya kurum yerleştirmeleri
- ödül çekilişleri
- sınırlı kontenjanlı başvurularda adil seçim

Sistem, süreci hem çok hızlandırır hem de teknik güveni ciddi biçimde artırır.

---

## Sorun Nedir?

Klasik dijital kura sistemlerinde ekranda isimlerin akması veya işlemin noter huzurunda yapılıyor olması, vatandaş açısından tek başına yeterli güveni sağlamaz.

Çünkü şu soru hep açık kalır:

**“Aynı sonucu ben kendi bilgisayarımda bağımsız olarak doğrulayabiliyor muyum?”**

Eğer cevap hayır ise, teknik olarak şu şüpheler tamamen kapanmaz:

- Yazılım doğru mu çalıştı?
- Liste son anda değiştirildi mi?
- Aynı yazılım herkese gösterilen ile gerçekten aynı mı?
- Bir hata veya kasıtlı müdahale var mı?

Bu proje, tam olarak bu güven açığını kapatmayı hedefler.

---

## Çözümün Mantığı

Bu projede çekiliş için rastgelelik, kurumun kendi sisteminden değil, dışarıdan alınan ve önceden bilinemeyen bir kaynaktan gelir:

**drand (Distributed Randomness Beacon)**

Böylece çekilişin seed değeri, çekilişten önce kurum tarafından seçilemez veya manipüle edilemez.

Akış şu şekildedir:

1. Katılımcı listesi CSV olarak hazırlanır.
2. Liste belirli ve herkesçe bilinen kurala göre sabitlenir.
3. Çekiliş zamanı önceden ilan edilir.
4. Bu zamana karşılık gelen drand round değeri hesaplanır.
5. drand API üzerinden o round’un randomness değeri alınır.
6. Bu değer Python tarafında seed olarak kullanılır.
7. Aynı liste ve aynı seed ile kazananlar seçilir.
8. Sonuçlar dosyaya yazılır.
9. İsteyen herkes aynı girdilerle aynı sonucu yeniden üretir.

---

## Neden Güvenilir?

Bu sistemin güvenilirliği “kuruma güven” mantığından değil, **doğrulanabilirlik** mantığından gelir.

### 1) Seed önceden bilinemediği için
Çekilişte kullanılacak rastgelelik değeri, önceden ilan edilen zamandaki drand çıktısından gelir. Bu değer çekiliş anından önce kesin olarak bilinemez.

### 2) Liste sabitlendiği için
Katılımcı listesi önceden paylaşılır veya en azından hash değeri yayımlanır. Böylece sonradan liste değiştirildiğinde bu durum tespit edilir.

### 3) Kod açık olduğu için
Çekilişi yapan kod herkese açık şekilde paylaşılır. Herkes aynı kodu inceleyebilir ve çalıştırabilir.

### 4) Sonuç tekrar üretilebilir olduğu için
Aynı CSV dosyası, aynı çekiliş zamanı ve aynı drand randomness değeri ile herkes birebir aynı sonucu üretir.

### 5) İnsan yorumuna değil deterministik işleyişe dayandığı için
Süreç, “ekranda isim akıyor, galiba doğru çalışıyor” yaklaşımına dayanmaz. Tam tersine, matematiksel olarak tekrar üretilebilir bir işleyişe dayanır.

---

## Bu Prototip Nasıl Çalışır?

Kodun genel akışı aşağıdaki gibidir:

### 1. Hedef zamandan drand round hesaplanır
Kod, verilen tarih/saat bilgisini Unix timestamp’e çevirir ve drand genesis zamanına göre ilgili round numarasını hesaplar.

### 2. drand randomness API’den alınır
Hesaplanan round için API çağrısı yapılır ve o round’a ait `randomness` değeri çekilir.

### 3. Katılımcı listesi sabitlenir
CSV dosyası okunur. Kod, ilk sütuna göre alfabetik sıralama yaparak listeyi standart hale getirir.

### 4. Seed atanır
Alınan drand randomness değeri `random.seed()` içine verilir.

### 5. Kazananlar seçilir
`random.sample()` ile istenen sayıda katılımcı seçilir.

### 6. Sonuç dosyaya yazılır
Kazananlar `kazananlar.csv` dosyasına kaydedilir.

---

## Kodun Öne Çıkan Noktaları

### Listeyi sabitleme
Kod şu yaklaşımı kullanır:

- CSV dosyasını okur
- ilk sütuna göre sıralar
- index’i sıfırlar

Böylece dosya farklı bilgisayarlarda aynı içerikle açıldığında aynı mantıksal sıra elde edilir.

### Aynı seed = aynı sonuç
Python’un sözde rastgele üreticisi deterministiktir. Aynı seed verildiğinde aynı sırayı üretir. Bu nedenle aynı girdi ile aynı çıktı oluşur.

### Tekrarlanabilirlik
Bu sistemin en güçlü tarafı budur. Sonuçların doğruluğu, sadece çekilişi yapan kurumun ekranına bakılarak değil, bağımsız tekrar çalıştırma ile test edilir.

---

## Katılımcılara Güven Nasıl Verilir?

İdeal süreç şu şekilde yürütülmelidir:

### Çekilişten önce
1. Katılımcı listesini kesinleştirin.
2. Listenin SHA-256 hash değerini yayımlayın.
3. Çekiliş zamanını ilan edin.
4. Kullanılacak kodu GitHub’da paylaşın.
5. Çekiliş kurallarını açıkça belirtin:
   - dosya formatı
   - sıralama kuralı
   - kazanan sayısı
   - yedek seçimi varsa yöntemi

### Çekilişten sonra
1. Kullanılan CSV dosyasını yayımlayın veya zaten yayımlanmışsa doğrulayın.
2. drand round ve randomness değerini paylaşın.
3. Çıkan sonuç dosyasını paylaşın.
4. Herkesin aynı sonucu tekrar üretmesini mümkün hale getirin.

Bu modelde güven, “kurumun beyanı” ile değil, **bağımsız doğrulama imkânı** ile oluşur.

---

## Kurulum

Python 3 önerilir.

Gerekli paketler:

```bash
pip install pandas requests
```

---

## Kullanım

Önce bir `katilimcilar.csv` dosyası hazırlayın.

Örnek kullanım mantığı:

```python
input_csv = "katilimcilar.csv"
cekilis_zamani = "01-03-2026 13:00:00"
kisi_sayisi = 10000
```

Ardından:

```bash
python cekilis.py
```

Kod başarılı çalıştığında:

- hesaplanan drand round’u gösterir
- kullanılan seed değerini gösterir
- sonuçları `kazananlar.csv` içine yazar

---

## Örnek Doğrulama Senaryosu

Diyelim ki kurum şu 3 bilgiyi önceden ilan etti:

- katılımcı listesi hash değeri
- çekiliş zamanı: `10-03-2026 13:00:00`
- GitHub’daki kaynak kod

Çekiliş bittiğinde herkes şunları yapabilir:

1. CSV listesini indirir
2. Listenin hash’ini kontrol eder
3. Aynı kodu çalıştırır
4. Aynı zamanı kullanır
5. drand verisini aynı round için çeker
6. Sonuçların aynı çıkıp çıkmadığını kontrol eder

Eğer aynı çıkıyorsa süreç doğrulanmış olur.
Eğer farklı çıkıyorsa ya liste değişmiştir, ya kod farklıdır, ya da süreçte bir oynama vardır.

---

## Bu Prototipin Güçlü Yönleri

- çok basit bir mantığa dayanır
- hızlıdır
- dış rastgelelik kaynağı kullanır
- tekrar üretilebilir
- bağımsız doğrulanabilir
- geniş kitlelere açık kura sistemleri için uygundur
- düşük maliyetle uygulanabilir
- güven inşasını teknik zemine taşır

---

## Dikkat Edilmesi Gereken Noktalar

Bu repo bir **prototip** içerir. Gerçek kamu uygulamasında aşağıdaki konular ayrıca ele alınmalıdır:

### 1) Liste formatı çok net tanımlanmalıdır
CSV sütun adları, karakter kodlaması, boşluklar, mükerrer kayıtlar, büyük-küçük harf farkları ve Türkçe karakter normalizasyonu gibi detaylar standartlaştırılmalıdır.

### 2) Hash mutlaka paylaşılmalıdır
Liste sonradan değiştirilmesin diye yalnızca dosya paylaşmak değil, dosyanın hash’ini önceden ilan etmek gerekir.

### 3) Yedek liste yöntemi açık olmalıdır
Asil ve yedek adaylar aynı algoritmayla, tek kuralla ve baştan ilan edilmiş şekilde belirlenmelidir.

### 4) API erişim bağımlılığı düşünülmelidir
Çekiliş anında dış API’ye erişim sorunu yaşanırsa, round bilgisi ve randomness sonradan da doğrulanabilecek biçimde kayıt altına alınmalıdır.

### 5) Bağımsız denetim yararlı olur
Kod açık kaynak olsa da, kamu kullanımından önce bağımsız yazılım güvenliği ve süreç denetimi yapılması faydalıdır.

---

## Özet

Bu proje şunu savunur:

Kamuya açık bir kura sisteminde asıl güven unsuru, işlemin yavaş yapılması veya yalnızca törensel gözetim değildir.

Asıl güven unsuru şudur:

**Aynı girdilerle aynı sonucu herkesin bağımsız olarak doğrulayabilmesi.**

Bu nedenle bu yaklaşım, dijital kura süreçlerinde güveni söylemden çıkarıp teknik ispat düzeyine taşımayı hedefler.

---

## Lisans

MIT License.

---

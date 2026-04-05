# Belediye Şikayet Sistemi

Vatandaşların belediyeye şikayet ve talep iletebileceği, yapay zeka destekli akıllı bir web tabanlı şikayet yönetim platformu.

---

## Proje Hakkında

Belediye Şikayet Sistemi; vatandaşların belediye hizmetleriyle ilgili şikayetlerini kolayca iletmesini, yetkililerin bu şikayetleri etkin biçimde yönetmesini ve yapay zeka destekli analizlerle süreçlerin iyileştirilmesini sağlar.

Sistem; doğal dil işleme (NLP), harita görselleştirme ile modern bir şikayet yönetimi deneyimi sunar.

---

## Özellikler

- **Şikayet Gönderme** — Vatandaşlar kategori seçerek şikayetlerini kolayca iletebilir
- **Harita Görselleştirme** — Folium ile şikayetlerin harita üzerinde görüntülenmesi
- **Türkçe NLP** — Zemberek ve NLTK ile Türkçe metin işleme ve kategori tespiti
- **İstatistik & Raporlama** — Şikayet yoğunluğu, durum takibi ve istatistiksel göstergeler
- **Rol Tabanlı Yetkilendirme** — Vatandaş, yetkili ve yönetici rolleri
- **Durum Takibi** — Vatandaşlar şikayetlerinin güncel durumunu takip edebilir

---

## Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| **Backend** | Django 6.0, Python |
| **Yapay Zeka** | Transformers, Scikit-learn |
| **NLP** | Zemberek (Türkçe), NLTK, NLTK Stopwords |
| **Harita** | Folium, Branca |
| **Veri İşleme** | Pandas, NumPy, Matplotlib |
| **Frontend** | HTML, CSS, JavaScript |
| **Veritabanı** | Django ORM (SQLite / PostgreSQL) |

---

## Kurulum

### Gereksinimler

- Python 3.10+
- pip

### Adımlar

```bash
# 1. Repoyu klonla
git clone https://github.com/emre-geris/Belediye_Sikayet_Sistemi.git
cd Belediye_Sikayet_Sistemi

# 2. Sanal ortam oluştur ve aktif et
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Veritabanı migrasyonlarını çalıştır
cd sikayet_sistemi
python manage.py migrate

# 5. Süper kullanıcı oluştur
python manage.py createsuperuser

# 6. Sunucuyu başlat
python manage.py runserver
```

Tarayıcıda `http://127.0.0.1:8000` adresine git.

---

## Kullanıcı Rolleri

| Rol | Yetkiler |
|-----|----------|
| **Vatandaş** | Şikayet gönderme, kendi şikayetlerini takip etme |
| **Yetkili** | Şikayetleri görüntüleme, durum güncelleme, yorum ekleme |
| **Yönetici** | Tüm sistem erişimi, kullanıcı yönetimi, raporlama |

Varsayılan giriş bilgileri için `Roller_ve_bilgiler.md` dosyasına bakın.

---

## Proje Yapısı

```
Belediye_Sikayet_Sistemi/
├── sikayet_sistemi/          # Ana Django projesi
│   ├── manage.py
│   ├── sikayet_sistemi/      # Proje ayarları
│   └── ...                   # Uygulama modülleri
├── requirements.txt          # Python bağımlılıkları
├── Roller_ve_bilgiler.md     # Rol ve kullanıcı bilgileri
└── README.md
```

---

## Lisans

Bu proje akademik amaçlı geliştirilmiştir.

---

## Geliştiriciler

**Emre Geriş**
**Berkay Öztürk**
**Bilal Khanzar**
**Muhammed Emir Tel**
**Hasan Erkeş**

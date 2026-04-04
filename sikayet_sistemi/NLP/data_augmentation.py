import pandas as pd
from google import genai
import time

# 1. API Ayarları (YENİ SİSTEM)
API_KEY = "GIZLI_API_ANAHTARI_BURAYA_GELECEK"
client = genai.Client(api_key=API_KEY)

# 2. Mevcut Veri Setini Oku (Dosya adını kontrol et)
dosya_adi = "sikayetler.csv"
df = pd.read_csv(dosya_adi)

# 3. Zayıf Kategoriler ve Üretilecek Miktarlar
eksik_kategoriler = {
    "Planlama ve Kentsel Gelişim": 200,
    "Sağlık ve Hijyen": 200,
    "ASKİ": 200,
    "Sosyal Yardımlar": 200
}

yeni_veriler = []

print("🤖 YENİ NESİL LLM Veri Üretim Motoru Başlatıldı...\n")

# 4. Her kategori için yapay zekaya prompt gönderiyoruz
for kategori, miktar in eksik_kategoriler.items():
    print(f"[{kategori}] kategorisi için {miktar} adet sentetik şikayet üretiliyor...")
    
    prompt = f"""
    Sen İstanbul veya Ankara'da yaşayan, belediyenin hizmetlerinden şikayetçi olan gerçek bir vatandaşsın.
    Bana '{kategori}' kategorisine tam uyacak şekilde {miktar} adet farklı şikayet cümlesi yaz.
    
    Kurallar:
    1. Çok resmi dil KULLANMA. Günlük konuşma dili, bazen hafif sinirli bir ton kullan.
    2. Arada sırada ufak tefek yazım yanlışları yapabilirsin (gerçekçi olması için).
    3. Cümlelerin içinde rastgele ilçe veya mahalle isimleri geçsin (Örn: Keçiören, Kadıköy, Dikmen, Esenyurt).
    4. SADECE şikayet cümlelerini alt alta liste olarak ver. Başlık, numara, madde işareti (1., 2., -) veya ekstra açıklama kesinlikle yazma!
    """
    
    try:
        # YENİ KÜTÜPHANE İLE İSTEK ATMA
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Google'ın güncel ve hızlı modeli
            contents=prompt
        )
        
        uretilen_metinler = response.text.strip().split('\n')
        
        # Üretilen her cümleyi listemize ekle
        for metin in uretilen_metinler:
            # Gereksiz kısa veya boş satırları atla
            if len(metin.strip()) > 5: 
                yeni_veriler.append({"text": metin.strip(), "label": kategori})
                
        print("✓ Üretim başarılı.\n")
        time.sleep(2) # Google'ın güvenlik duvarına (Rate Limit) takılmamak için bekliyoruz
        
    except Exception as e:
        print(f"X Bir hata oluştu: {e}")

# 5. Üretilen yeni verileri DataFrame'e dönüştür ve eski veri setiyle birleştir
yeni_df = pd.DataFrame(yeni_veriler)
birlestirilmis_df = pd.concat([df, yeni_df], ignore_index=True)

# 6. Zenginleştirilmiş yeni veri setini kaydet
yeni_dosya_adi = "sikayetler_dengeli.csv"
birlestirilmis_df.to_csv(yeni_dosya_adi, index=False)

print(f"🎉 İşlem Tamam! Zenginleştirilmiş veri seti '{yeni_dosya_adi}' adıyla kaydedildi.")
print(f"Toplam eklenen sentetik şikayet sayısı: {len(yeni_df)}")
import folium
import joblib
import os
import webbrowser

# 1. Dondurulmuş Modelleri Yükle (Django ekibi sunucuyu başlattığında 1 kere çalışır)
print("🧠 Yapay Zeka modelleri harita için yükleniyor...")
vectorizer = joblib.load('vectorizer.pkl')
model_kategori = joblib.load('model_kategori.pkl')
model_oncelik = joblib.load('model_oncelik.pkl')

def sikayet_haritasi_olustur(sikayetler):
    """
    Bu fonksiyonu Django ekibi çağıracak. 
    İçine sözlük (dictionary) listesi halinde şikayetleri atacaklar.
    """
    
    # Haritayı başlat (Örnek başlangıç koordinatı: Ankara/Dikmen civarı)
    map = folium.Map(location=[41.0082, 28.9784], zoom_start=11, tiles="OpenStreetMap")
    folium.TileLayer('CartoDB positron').add_to(map)
        
    for veri in sikayetler:
        metin = veri['text']
        enlem = veri['lat']
        boylam = veri['lon']
        
        # 2. YAPAY ZEKA TAHMİNİ (Senin eserin!)
        # Temizleme fonksiyonun varsa burada metni temizleyebilirsin
        vektor = vectorizer.transform([metin])
        kategori = model_kategori.predict(vektor)[0]
        aciliyet = int(model_oncelik.predict(vektor)[0])
        
        # 3. ACİLİYETE GÖRE RENK BELİRLEME
        if aciliyet == 3:
            renk = "#e74c3c"  # Kırmızı (Tehlikeli ve acil durumlar için)
            yari_cap = 800
            aciliyet_metni = "YÜKSEK ACİLİYET"
        elif aciliyet == 2:
            renk = "#f39c12"  # Turuncu (Orta aciliyet için / Uyarı durumlar)
            yari_cap = 400
            aciliyet_metni = "ORTA ACİLİYET"
        else:
            renk = "#3498db"  # Mavi (Düşük aciliyet için / Bilgilendirme durumları)
            yari_cap = 200
            aciliyet_metni = "DÜŞÜK ACİLİYET"
            
        # 3. HARİTAYA DAİRE (CIRCLE) EKLE
        popup_html = f"""
        <b>Kategori:</b> {kategori}<br>
        <b>Durum:</b> <span style="color:{renk};">{aciliyet_metni}</span><br>
        <hr>
        <i>"{metin}"</i>
        """
        
        folium.Circle(
            location=[enlem, boylam],
            radius=yari_cap, # Dairenin büyüklüğü (metre cinsinden)
            color=renk,      # Dairenin dış çizgi rengi
            weight=2,        # Dış çizgi kalınlığı
            fill=True,       # İçi dolu olsun mu?
            fill_color=renk, # İç dolgu rengi
            fill_opacity=0.4,# İç dolgu şeffaflığı (Altındaki harita yollarını görebilmek için)
            popup=folium.Popup(popup_html, max_width=300),
            tooltip="Detay için tıkla"
        ).add_to(map)
        
    # Haritayı bir HTML dosyası olarak kaydet (Sen kendi bilgisayarında test etmek için)
    map.save("test_haritasi.html")
    
    # Django ekibi için haritanın HTML kodunu direkt döndür (Çok sevinecekler)
    return map._repr_html_()

# ---------------------------------------------------------
# LOCAL TEST ALANI
if __name__ == "__main__":
    test_verileri = [
        # 1. Beşiktaş (Barbaros Bulvarı) - Yüksek Aciliyet (Açık Rögar / Kaza Riski)
        {"text": "Beşiktaş Barbaros Bulvarı'nda açık bırakılan rögar kapağı yüzünden az kalsın kaza yapıyordum, çok tehlikeli!", 
         "lat": 41.0454, "lon": 29.0082},
         
        # 2. Kadıköy (Moda Sahili) - Orta Aciliyet (Gürültü Kirliliği)
        {"text": "Kadıköy Moda sahilinde gece yarısına kadar süren yüksek sesli müzik yüzünden uyuyamıyoruz, lütfen denetim yapılsın.", 
         "lat": 40.9781, "lon": 29.0255},
         
        # 3. Ümraniye (Merkez) - Düşük Aciliyet (Park ve Bahçe Bakımı)
        {"text": "Ümraniye Meydan'daki parkın bankları çok eskimiş ve kırık, yenilenmesini ve boyanmasını talep ediyoruz.", 
         "lat": 41.0256, "lon": 29.0989},
         
        # 4. Sarıyer (Hacıosman) - Yüksek Aciliyet (Sokak Hayvanları Tehditi / Güvenlik)
        {"text": "Sarıyer Hacıosman korusu girişinde saldırgan başıboş köpek sürüsü var, sabahları yürüyüş yapamıyoruz acil müdahale edilmeli.", 
         "lat": 41.1402, "lon": 29.0305},
         
        # 5. Esenyurt (Gişeler Mevkii) - Orta Aciliyet (Altyapı ve Asfalt)
        {"text": "Esenyurt bağlantı yolunda asfalt tamamen çökmüş durumda, devasa bir çukur var araçların altı sürtüyor.", 
         "lat": 41.0342, "lon": 28.6801}
    ]
    
    print("🗺️ Harita oluşturuluyor...")
    html_ciktisi = sikayet_haritasi_olustur(test_verileri)
    print("✅ İşlem tamam! Proje klasöründeki 'test_haritasi.html' dosyasını tarayıcıda açıp kontrol edebilirsin.")
    file_name = "test_haritasi.html"
    webbrowser.open('file://' + os.path.realpath(file_name))


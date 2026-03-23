import pandas as pd
# -*- coding: utf-8 -*-
from unicode_tr import unicode_tr
import re
from zemberek import TurkishSentenceExtractor, TurkishTokenizer
from zemberek.tokenization.token import Token
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
import joblib

# Veri Setini Yükleme ve CSV'ye Kaydetme

df = pd.read_csv("sikayetler_oncelikli.csv")
texts = df["text"]
y_kategori = df["label"]
y_oncelik = df["önem derecesi"]  
nltk.download('stopwords')
stopwords_list = set(stopwords.words('turkish'))
print(f"Eğitime giren toplam şikayet sayısı: {len(df)}")
# Veri Ön İşleme

def clean_text(texts):
    unwanted_list = [u"&bull;", u"&lsquo;",u",",u"?",u"!",u'"',u"'",u"‘",u"’",u"/",u"<",u">",u"|",u"“",";","&","(",")","=","+","-","\\","*",":","~","@","."]
    alpha_list = [u"a",u"b",u"c",u"ç",u"d",u"e",u"f",u"g",u"ğ",u"h",u"ı",u"i",u"j",u"k",u"l",u"m",u"n",u"o",u"ö",u"p",u"q",u"r",u"s",u"ş",u"t",u"u",u"ü",u"v",u"w",u"x",u"y",u"z"," ",]

    # küçük harfe çeviriliyor
    sentences = unicode_tr(texts).lower()
    txt = sentences.replace(u"â", u"a").lower()
    
    # farklı karakterler siliniyor
    for unwanted_char in unwanted_list:
        # txt = txt.replace(uw,' ')
        # "Ankara'da" gibi tırnak kaldırıldığında "Ankara da" şeklinde oluşan aradaki boşluk birleştirildi.
        txt = txt.replace(unwanted_char, "")

    # geçerli harf listesi dışındaki harfler siliniyor
    chars = list(set(txt))
    for char in chars:
        if not char in alpha_list:
            txt = txt.replace(char, "")

    return txt

def remove_URL(texts):
    pattern_url = r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
    text_clean = re.sub(pattern_url, "", texts)
    return text_clean

def remove_email(texts):
    pattern_email = "\S*@\S*\s?"
    text_clean = re.sub(pattern_email, "", texts)
    return text_clean

# Cümle Ayırma ve Tokenizasyon

extractor = TurkishSentenceExtractor()
tokenizer = TurkishTokenizer.builder().accept_all().ignore_types(
    [Token.Type.NewLine,
     Token.Type.SpaceTab,
     Token.Type.Punctuation]).build()

for text in texts:
    #print(f"Orijinal Şikayet: {text}")
    #print("-" * 50) 
    sentences = extractor.from_paragraph(str(text)) # Şikayeti cümlelere ayır
    
    for sentence in sentences:
        #print(f"Orijinal Cümle: {sentence}") # Şikayetin cümlelerini yazdır
        tokens = tokenizer.tokenize(sentence) # Cümleleri tokenlara ayır
        words = [clean_text(token.content) for token in tokens] # Tokenları temizle
        #print(f"Tokenize Edilmiş Hali: {words}\n") 

        # Stop Words'leri Kaldırdık
        #print("words_filtered")
        words_filtered = []
        for w in words:
            if w not in stopwords_list:
                words_filtered.append(w)

        # print(words_filtered)
        # print("\n")
                
# TF-IDF Vektörizasyonu

tfidf = TfidfVectorizer()
result = tfidf.fit_transform(texts)

# Veriyi Eğitim ve Test Olarak Ayırma / ML Algoritmalarını Karşılaştırma

#Veriyi %80 Eğitim (Train) ve %20 Test (Sınav) olarak bölüyoruz
X_train, X_test, y_train, y_test = train_test_split(result, y_kategori, test_size=0.2, random_state=42)

# 4. Eğitim ve Test Süreci

# Çift Başlı Model Eğitimi
print("🧠 1. Model Eğitiliyor: Kategori Sınıflandırıcı (SVM)...")
model_kategori = LinearSVC(class_weight='balanced', max_iter=2000)
model_kategori.fit(result, y_kategori)

print("🧠 2. Model Eğitiliyor: Aciliyet Sınıflandırıcı (SVM)...")
model_oncelik = LinearSVC(class_weight='balanced', max_iter=2000)
model_oncelik.fit(result, y_oncelik)

print("✅ Modeller başarıyla eğitildi ve kullanıma hazır!\n")
print("-" * 50)

# 4. CANLI TEST (Harita Demosunun Altyapısı)
# Bu fonksiyon, web sitesinden gelen veriyi arka planda nasıl işleyeceğimizin simülasyonudur.
def sikayet_analiz_et(yeni_sikayet):
    temiz_text = clean_text(yeni_sikayet)
    # 1. Gelen metni aynı TF-IDF filtresinden geçir
    vektor = tfidf.transform([temiz_text])
    
    # 2. İki modelden de tahmin iste
    tahmin_kategori = model_kategori.predict(vektor)[0]
    tahmin_oncelik = model_oncelik.predict(vektor)[0]
    
    # 3. Sonucu haritaya (şimdi terminale) bas
    print(f"📝 Gelen Şikayet: '{yeni_sikayet}'")
    print(f"🔍 Temizlenmiş Hali: '{temiz_text}'")
    print(f"🏷️ Kategori     : {tahmin_kategori}")
    
    # Aciliyete göre renk/ikon belirleme mantığı (Haritada çok işimize yarayacak)
    if tahmin_oncelik == 3:
        renk = "🔴 YÜKSEK (Kırmızı Pin)"
    elif tahmin_oncelik == 2:
        renk = "🟡 ORTA (Sarı Pin)"
    else:
        renk = "🟢 DÜŞÜK (Yeşil Pin)"
        
    print(f"🚨 Aciliyet     : {tahmin_oncelik} - {renk}\n")

# 5. Modelin Harita Entegrasyonu İçin Kaydedilmesi

print("\n📦 Modeller harita entegrasyonu için donduruluyor...")
# 1. Kelime çeviriciyi (Vectorizer) kaydet
joblib.dump(tfidf, 'vectorizer.pkl')

# 2. Kategori modelini kaydet
joblib.dump(model_kategori, 'model_kategori.pkl')

# 3. Aciliyet modelini kaydet
joblib.dump(model_oncelik, 'model_oncelik.pkl')

print("✅ 'vectorizer.pkl', 'model_kategori.pkl' ve 'model_oncelik.pkl' dosyaları proje klasörüne başarıyla kaydedildi!")
print("🚀 Artık harita backend'i bu zekayı kullanabilir.")
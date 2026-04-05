import sys
import typing
# Zemberek (antlr4) ve Python 3.13 Uyumsuzluğu İçin Sihirli Yama
sys.modules['typing.io'] = typing
import pandas as pd
import numpy as np
# -*- coding: utf-8 -*-
from unicode_tr import unicode_tr
import re
from zemberek import TurkishSentenceExtractor, TurkishTokenizer
from zemberek.tokenization.token import Token
import nltk
from nltk.corpus import stopwords
from sklearn.metrics import classification_report
from gensim.models import Word2Vec
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
import joblib

# 1. Veri Setini Yükleme ve CSV'ye Kaydetme
df = pd.read_csv("sikayetler_oncelikli.csv")
texts = df["text"]
y_kategori = df["label"]
y_oncelik = df["önem derecesi"]  
nltk.download('stopwords', quiet=True)
stopwords_list = set(stopwords.words('turkish'))
print(f"Eğitime giren toplam şikayet sayısı: {len(df)}")

# 2. Veri Ön İşleme
def clean_text(texts):
    unwanted_list = [u"&bull;", u"&lsquo;",u",",u"?",u"!",u'"',u"'",u"‘",u"’",u"/",u"<",u">",u"|",u"“",";","&","(",")","=","+","-","\\","*",":","~","@","."]
    alpha_list = [u"a",u"b",u"c",u"ç",u"d",u"e",u"f",u"g",u"ğ",u"h",u"ı",u"i",u"j",u"k",u"l",u"m",u"n",u"o",u"ö",u"p",u"q",u"r",u"s",u"ş",u"t",u"u",u"ü",u"v",u"w",u"x",u"y",u"z"," ",]

    sentences = unicode_tr(texts).lower()
    txt = sentences.replace(u"â", u"a").lower()
    
    for unwanted_char in unwanted_list:
        txt = txt.replace(unwanted_char, "")

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
    pattern_email = r"\S*@\S*\s?"
    text_clean = re.sub(pattern_email, "", texts)
    return text_clean

# 3. Cümle Ayırma ve Tokenizasyon (Hata 1 Düzeltildi)
print("\n⚙️ Zemberek ile şikayetler tokenlara ayrılıyor...")
extractor = TurkishSentenceExtractor()
tokenizer = TurkishTokenizer.builder().accept_all().ignore_types(
    [Token.Type.NewLine, Token.Type.SpaceTab, Token.Type.Punctuation]).build()

tokenized_sentences = [] 

for text in texts:
    sikayet_kelimeleri = [] 
    sentences = extractor.from_paragraph(str(text)) 
    
    for sentence in sentences:
        tokens = tokenizer.tokenize(sentence) 
        words = [clean_text(token.content) for token in tokens] 

        for w in words:
            if w and w not in stopwords_list:
                sikayet_kelimeleri.append(w) # <-- Boş liste sorunu çözüldü

    tokenized_sentences.append(sikayet_kelimeleri)
                
# 4. WORD2VEC Vektörleştirme
print("🧠 Word2Vec Dil Modeli eğitiliyor...")
w2v_model = Word2Vec(sentences=tokenized_sentences, vector_size=100, window=5, min_count=1, workers=4)

def get_document_vector(words, model, vector_size):
    valid_words = [word for word in words if word in model.wv.key_to_index]
    if valid_words:
        return np.mean(model.wv[valid_words], axis=0)
    else:
        return np.zeros(vector_size)

print("📊 Şikayetler Word2Vec üzerinden sayısal vektör matrisine (X) dönüştürülüyor...")
X = np.array([get_document_vector(words, w2v_model, 100) for words in tokenized_sentences])

# 5. EĞİTİM VE TEST SÜRECİ
X_train, X_test, y_train, y_test, y_onc_train, y_onc_test = train_test_split(
    X, y_kategori, y_oncelik, test_size=0.2, random_state=42
)

print("🧠 1. Model Eğitiliyor: Kategori Sınıflandırıcı (SVM)...")
model_kategori = LinearSVC(class_weight='balanced', max_iter=2000, random_state=42)
model_kategori.fit(X_train, y_train)

print("🧠 2. Model Eğitiliyor: Aciliyet Sınıflandırıcı (SVM)...")
model_oncelik = LinearSVC(class_weight='balanced', max_iter=2000, random_state=42)
model_oncelik.fit(X_train, y_onc_train) 

print("✅ Modeller başarıyla eğitildi ve kullanıma hazır!\n")
print("-" * 50)

print("📊 KATEGORİ MODELİ BAŞARI RAPORU (TEST SETİ):")
y_kategori_tahmin = model_kategori.predict(X_test)
print(classification_report(y_test, y_kategori_tahmin))

print("-" * 50)

print("📊 ACİLİYET MODELİ BAŞARI RAPORU (TEST SETİ):")
y_oncelik_tahmin = model_oncelik.predict(X_test)
print(classification_report(y_onc_test, y_oncelik_tahmin))
print("-" * 50)

# 6. CANLI TEST
def sikayet_analiz_et(yeni_sikayet):
    yeni_kelimeler = []
    sentences = extractor.from_paragraph(str(yeni_sikayet))
    for sentence in sentences:
        tokens = tokenizer.tokenize(sentence)
        words = [clean_text(token.content) for token in tokens]
        for w in words:
            if w and w not in stopwords_list:
                yeni_kelimeler.append(w)
                
    vektor = get_document_vector(yeni_kelimeler, w2v_model, 100).reshape(1, -1)
    
    tahmin_kategori = model_kategori.predict(vektor)[0]
    tahmin_oncelik = model_oncelik.predict(vektor)[0]
    
    print(f"📝 Gelen Şikayet: '{yeni_sikayet}'")
    print(f"🔍 Zemberek Çıktısı: {yeni_kelimeler}") # <-- Hata 3 Düzeltildi
    print(f"🏷️ Kategori     : {tahmin_kategori}")
    
    if tahmin_oncelik == 3:
        renk = "🔴 YÜKSEK (Kırmızı Pin)"
    elif tahmin_oncelik == 2:
        renk = "🟡 ORTA (Sarı Pin)"
    else:
        renk = "🟢 DÜŞÜK (Yeşil Pin)"
        
    print(f"🚨 Aciliyet     : {tahmin_oncelik} - {renk}\n")

if __name__ == "__main__":
    # Hızlı bir demo yapalım
    sikayet_analiz_et("Sokağımızdaki su borusu patladı ve her yeri su bastı, acil yardım lazım!")

# 7. MODELLERİ KAYDETME
print("\n📦 Modeller harita entegrasyonu için donduruluyor...")

w2v_model.save('word2vec.pkl') 
joblib.dump(model_kategori, 'model_kategori.pkl')
joblib.dump(model_oncelik, 'model_oncelik.pkl')

print("✅ 'word2vec.pkl', 'model_kategori.pkl' ve 'model_oncelik.pkl' dosyaları başarıyla kaydedildi!")
print("🚀 Artık harita backend'i bu zekayı kullanabilir.")
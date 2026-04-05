import sys
import typing
sys.modules['typing.io'] = typing
import numpy as np
import re
from unicode_tr import unicode_tr
from zemberek import TurkishSentenceExtractor, TurkishTokenizer
from zemberek.tokenization.token import Token
import nltk
from nltk.corpus import stopwords
from gensim.models import Word2Vec
import joblib
import os

# Dosya yollarını dinamik ayarlayalım (Django nereden çalışırsa çalışsın bulsun)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
W2V_PATH = os.path.join(BASE_DIR, 'word2vec.pkl')
KAT_MODEL_PATH = os.path.join(BASE_DIR, 'model_kategori.pkl')
ONC_MODEL_PATH = os.path.join(BASE_DIR, 'model_oncelik.pkl')

# 1. Modelleri Hafızaya Yükle (Sadece 1 Kere Çalışır)
w2v_model = Word2Vec.load(W2V_PATH)
model_kategori = joblib.load(KAT_MODEL_PATH)
model_oncelik = joblib.load(ONC_MODEL_PATH)

# Zemberek ve Stopwords Ayarları
nltk.download('stopwords', quiet=True)
stopwords_list = set(stopwords.words('turkish'))
extractor = TurkishSentenceExtractor()
tokenizer = TurkishTokenizer.builder().accept_all().ignore_types(
    [Token.Type.NewLine, Token.Type.SpaceTab, Token.Type.Punctuation]).build()

# 2. Metin Temizleme Fonksiyonları
def clean_text(texts):
    unwanted_list = [u"&bull;", u"&lsquo;",u",",u"?",u"!",u'"',u"'",u"‘",u"’",u"/",u"<",u">",u"|",u"“",";","&","(",")","=","+","-","\\","*",":","~","@","."]
    alpha_list = [u"a",u"b",u"c",u"ç",u"d",u"e",u"f",u"g",u"ğ",u"h",u"ı",u"i",u"j",u"k",u"l",u"m",u"n",u"o",u"ö",u"p",u"q",u"r",u"s",u"ş",u"t",u"u",u"ü",u"v",u"w",u"x",u"y",u"z"," "]
    sentences = unicode_tr(texts).lower()
    txt = sentences.replace(u"â", u"a").lower()
    for unwanted_char in unwanted_list:
        txt = txt.replace(unwanted_char, "")
    chars = list(set(txt))
    for char in chars:
        if not char in alpha_list:
            txt = txt.replace(char, "")
    return txt

def get_document_vector(words, model, vector_size):
    valid_words = [word for word in words if word in model.wv.key_to_index]
    if valid_words:
        return np.mean(model.wv[valid_words], axis=0)
    else:
        return np.zeros(vector_size)

# 3. Backend Ekibinin Çağıracağı ANA FONKSİYON
def sikayeti_degerlendir(metin):
    """
    Django'dan gelen ham metni alır, temizler, vektörleştirir ve tahmin döndürür.
    Kullanım: kategori, oncelik = sikayeti_degerlendir("su patladı")
    """
    yeni_kelimeler = []
    sentences = extractor.from_paragraph(str(metin))
    for sentence in sentences:
        tokens = tokenizer.tokenize(sentence)
        words = [clean_text(token.content) for token in tokens]
        for w in words:
            if w and w not in stopwords_list:
                yeni_kelimeler.append(w)
                
    vektor = get_document_vector(yeni_kelimeler, w2v_model, 100).reshape(1, -1)
    
    tahmin_kategori = model_kategori.predict(vektor)[0]
    tahmin_oncelik = model_oncelik.predict(vektor)[0]
    
    # Backend'in kolayca kullanabilmesi için bir sözlük (dictionary) döndürüyoruz
    return {
        "kategori": tahmin_kategori,
        "oncelik_derecesi": int(tahmin_oncelik)
    }
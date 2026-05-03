import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sikayet_sistemi"))

from NLP.llm_classifier import process_complaint, HUMAN_REVIEW_THRESHOLD

DIVIDER = "=" * 65

def print_result(text: str, result: dict):
    flag = "  *** İNSAN ONAYINA GÖNDER ***" if result["needs_human_review"] else ""
    print(f"\n{DIVIDER}")
    print(f"  Şikayet    : {text}")
    print(DIVIDER)

    rp = result.get("reasoning_path", {})
    print(f"  Kategori   : {result['kategori']}")
    print(f"  Aciliyet   : {result['aciliyet']}")
    print(f"  Muhakeme   : {result['muhakeme']}")
    print(f"  Özet       : {result['ozet']}")
    print(f"  Güven      : {result['confidence_score']:.2f} / 1.00  (eşik: {HUMAN_REVIEW_THRESHOLD}){flag}")
    print()
    print(f"  Ham Yanıt  :\n  {result['_raw']}")


print(f"Belediye Şikayet Sınıflandırıcı — çıkmak için 'q'\n"
      f"(Güven skoru < {HUMAN_REVIEW_THRESHOLD} → insan onayı flag'i)\n")

while True:
    text = input("Şikayet: ").strip()
    if text.lower() == "q":
        break
    if not text:
        continue
    print("Analiz ediliyor...")
    try:
        result = process_complaint(text)
        print_result(text, result)
    except Exception as e:
        print(f"  HATA: {e}")

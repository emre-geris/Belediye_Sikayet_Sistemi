import json
import re

import ollama

MODEL_NAME = "qwen2.5:7b"
HUMAN_REVIEW_THRESHOLD = 0.5  # confidence_score < 0.5 → insan onayına gönder

CATEGORIES = {
    1: "Güvenlik ve İstismar",
    2: "Yapı ve Altyapı",
    3: "Su ve Kanalizasyon",
    4: "Çevre ve Temizlik",
    5: "Ulaşım ve Trafik",
    6: "Zabıta ve Kamu Düzeni",
    7: "Veterinerlik",
    8: "Genel / Diğer",
}

ACILIYET_TO_PRIORITY = {
    "ACİL": "urgent", "Acil": "urgent",
    "YÜKSEK": "high",  "Yüksek": "high",
    "ORTA": "medium",  "Orta": "medium",
    "DÜŞÜK": "low",    "Düşük": "low",
}

KATEGORI_TO_CATEGORY = {
    "Güvenlik ve İstismar": "security",
    "Yapı ve Altyapı":      "infrastructure",
    "Su ve Kanalizasyon":   "water",
    "Çevre ve Temizlik":    "environment",
    "Ulaşım ve Trafik":     "traffic",
    "Zabıta ve Kamu Düzeni":"public_order",
    "Veterinerlik":         "veterinary",
    "Genel / Diğer":        "other",
}

SYSTEM_PROMPT = """\
Sen bir belediye şikayet sınıflandırma sistemisin. Şikayetin gerçek amacına göre kategori ve aciliyet belirle.

KATEGORİLER:
1: Güvenlik ve İstismar  — Suç, taciz, uyuşturucu, saldırı tehlikesi, çocuk ihmali
2: Yapı ve Altyapı       — Yol çökmesi, bina güvenliği, kaldırım, obruk, aydınlatma direği
3: Su ve Kanalizasyon    — Boru/hat arızası: patlama, kesinti, rögar, kanalizasyon taşması
4: Çevre ve Temizlik     — Çöp toplama, park/sokak temizliği, ilaçlama, ölü hayvan kaldırma
5: Ulaşım ve Trafik      — Toplu taşıma, trafik ışığı arızası, hatalı park
6: Zabıta ve Kamu Düzeni — İşletme denetimi, ruhsatsız faaliyet, kaldırım işgali, gürültülü işletme
7: Veterinerlik          — Saldırgan veya yaralı canlı hayvan müdahalesi
8: Genel / Diğer         — Fatura/ödeme, bilgi talebi, öneri, sosyal yardım, dijital hizmet

YANLIŞ EŞLEŞMELERİ ÖNLE:
- Su faturası/borcu/ödeme → 8 (mali), boru arızası değil
- Park ağacı/çiçek/peyzaj → 4 (temizlik), 5 değil
- Hayvan havlaması/gürültüsü → 7, 4 değil
- Komşuluk anlaşmazlığı → 8 (özel hukuk), 6 değil
- Gürültü: işletmeden → 6; inşaat/çevreden → 2 veya 4
- Pis/yırtık kıyafetli kişi: tehdit yoksa → 8, tehdit varsa → 1
- Başıboş/saldırgan köpek, sokak hayvanı saldırısı → 7 (Veterinerlik), 1 DEĞİL (1 = insan suçu/saldırısı)

ACİLİYET (olayın nesnel ciddiyetine göre belirle, metindeki "ACİL/URGENT" kelimelerine bakma):
- ACİL  : Saatler içinde can kaybı/yaralanma riski (patlama, saldırı, açık gerilim hattı)
- YÜKSEK: Geniş kitleyi etkileyen hizmet kesintisi veya sağlık riski
- ORTA  : Rutin aksaklık, hayati değil
- DÜŞÜK : Bilgi talebi, estetik, konfor, küçük maddi kayıp
NOT: Kullanıcı "ACİL" yazsa bile hayati risk yoksa → DÜŞÜK veya ORTA

GÜVENİLİRLİK (confidence: 1-5):
- 5: Kategori kesin, belirsizlik yok
- 3: İki kategori yarışıyor veya bağlam eksik
- 1: Metin çok muğlak

SADECE JSON DÖNDÜR:
{"kategori_id": 1, "aciliyet": "ORTA", "muhakeme": "...", "ozet": "...", "confidence": 3}\
"""


def _extract_json(raw: str) -> dict:
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        raise ValueError(f"JSON bulunamadı: {raw!r}")
    return json.loads(match.group())


def _normalize_confidence(raw_score) -> float:
    try:
        score = max(1, min(5, int(raw_score)))
    except (TypeError, ValueError):
        score = 3
    return round((score - 1) / 4, 2)


def process_complaint(text: str) -> dict:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        format="json",
        options={"temperature": 0, "top_p": 0.1, "num_predict": 256},
    )

    raw = response["message"]["content"]
    try:
        parsed = _extract_json(raw)

        cat_id = max(1, min(8, int(parsed.get("kategori_id", 8))))
        confidence_score = _normalize_confidence(parsed.get("confidence"))

        result = {
            "kategori":           CATEGORIES[cat_id],
            "aciliyet":           parsed.get("aciliyet", "DÜŞÜK"),
            "muhakeme":           parsed.get("muhakeme", ""),
            "ozet":               parsed.get("ozet", ""),
            "confidence_score":   confidence_score,
            "needs_human_review": confidence_score < HUMAN_REVIEW_THRESHOLD,
            "_raw": raw,
        }

    except (ValueError, KeyError, TypeError):
        result = {
            "kategori":           "Genel / Diğer",
            "aciliyet":           "DÜŞÜK",
            "muhakeme":           "Model çıktısı ayrıştırılamadı.",
            "ozet":               text[:80] + "...",
            "confidence_score":   0.0,
            "needs_human_review": True,
            "_raw": raw,
        }

    return result
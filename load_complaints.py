#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, "/c/Users/emreg/OneDrive/Desktop/sikayet_sistemi/sikayet_sistemi")
django.setup()

from apps.complaints.models import Complaint  # type: ignore[import-not-found]
from apps.users.models import CustomUser  # type: ignore[import-not-found]

# Eski test şikayetlerini temizle
Complaint.objects.filter(title__contains="Maltepe").delete()
Complaint.objects.filter(title__contains="Kadıköy").delete()
Complaint.objects.filter(title__contains="Beşiktaş").delete()

print("✓ Eski şikayetler silindi")

# User al
user = CustomUser.objects.first()

# Yeni şikayetler - UTF-8 doğru şekilde
test_complaints = [
    {
        "title": "Maltepe - Kaldırım Hasarı",
        "description": "Maltepe ilçesinde kaldırım yüzeyi bozulmuş durumda. Pazar günü burada yürürken sol ayağım döndü.",
        "category": "infrastructure",
        "city": "İstanbul",
        "district": "Maltepe",
        "address": "Mimar Sinan Sokak No:45",
        "latitude": 40.9647,
        "longitude": 29.1364,
        "priority": "high",
        "status": "new",
        "user": user,
    },
    {
        "title": "Kadıköy - Trafik Sorunu",
        "description": "Kadıköy Mehmet Hüseyinpaşa Caddesi çok kalabalık ve trafik düzensiz. Sürücüler kurallara uymuyor.",
        "category": "traffic",
        "city": "İstanbul",
        "district": "Kadıköy",
        "address": "Mehmet Hüseyinpaşa Cad. No:100",
        "latitude": 40.9891,
        "longitude": 29.0289,
        "priority": "medium",
        "status": "new",
        "user": user,
    },
    {
        "title": "Beşiktaş - Su Kaçağı",
        "description": "Beşiktaş Barbaros Bulvarında hafta haftaya su kaçakları oluşuyor. Su boşa gidiyor.",
        "category": "water",
        "city": "İstanbul",
        "district": "Beşiktaş",
        "address": "Barbaros Bulvarı No:250",
        "latitude": 41.0758,
        "longitude": 29.0019,
        "priority": "urgent",
        "status": "new",
        "user": user,
    },
]

for data in test_complaints:
    complaint = Complaint.objects.create(**data)
    print(f"✓ Oluşturuldu: {complaint.title} - {complaint.district}")

print("\n✓✓✓ Tüm yeni şikayetler UTF-8 encoding ile eklendi!")

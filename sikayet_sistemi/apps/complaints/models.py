from django.db import models
from django.conf import settings

class Complaint(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
        ('urgent', 'Acil'),
    ]

    STATUS_CHOICES = [
        ('new', 'Yeni'),
        ('in_progress', 'İnceleniyor'),
        ('resolved', 'Çözüldü'),
        ('rejected', 'Reddedildi'),
    ]

    CATEGORY_CHOICES = [
        ('infrastructure', 'Altyapı'),
        ('traffic', 'Trafik'),
        ('pothole', 'Çukur'),
        ('water', 'Su Kaçağı'),
        ('trash', 'Çöp'),
        ('other', 'Diğer'),
    ]

    title = models.CharField(
        max_length=255,
        verbose_name="Şikayet Başlığı"
    )
    description = models.TextField(
        verbose_name="Şikayet Açıklaması"
    )
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        verbose_name="Kategori"
    )
    city = models.CharField(
        max_length=100,
        verbose_name="İl"
    )
    district = models.CharField(
        max_length=100,
        verbose_name="İlçe"
    )
    address = models.TextField(
        verbose_name="Adres"
    )
    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Enlem"
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Boylam"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Öncelik Seviyesi"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Durum"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='complaints',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )

    class Meta:
        verbose_name = "Şikayet"
        verbose_name_plural = "Şikayetler"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.district}"

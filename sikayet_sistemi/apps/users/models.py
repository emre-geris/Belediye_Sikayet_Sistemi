from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Özel kullanıcı modeli - yönetici ve normal kullanıcı ayrımı için
    TC Kimlik Numarası ile giriş yapılır, username email'den otomatik oluşturulur
    """
    
    USER_TYPE_CHOICES = (
        ('user', 'Kullanıcı'),
        ('admin', 'Belediye Çalışanı'),
        ('system_admin', 'Sistem Yöneticisi'),
    )

    user_type = models.CharField(
        max_length=12,
        choices=USER_TYPE_CHOICES,
        default='user',
        verbose_name='Kullanıcı Türü'
    )
    phone = models.CharField(
        max_length=15,
        verbose_name='Telefon Numarası'
    )
    tc_id = models.CharField(
        max_length=11,
        unique=True,
        verbose_name='TC Kimlik Numarası'
    )
    address = models.TextField(
        verbose_name='Adres'
    )
   
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Oluşturulma Tarihi'
    )
    
    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()}"
    
    def is_admin_user(self):
        return self.user_type in ('admin', 'system_admin')

    def is_system_admin(self):
        return self.user_type == 'system_admin'


class Notification(models.Model):
    """Kullanıcıya gösterilecek panel bildirimleri."""

    TYPE_CHOICES = (
        ('status_update', 'Durum Güncellemesi'),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Kullanıcı',
    )
    complaint = models.ForeignKey(
        'complaints.Complaint',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        verbose_name='Şikayet',
    )
    notification_type = models.CharField(
        max_length=40,
        choices=TYPE_CHOICES,
        default='status_update',
        verbose_name='Bildirim Türü',
    )
    title = models.CharField(
        max_length=150,
        verbose_name='Başlık',
    )
    message = models.TextField(
        verbose_name='Mesaj',
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Okundu mu',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Oluşturulma Tarihi',
    )

    class Meta:
        verbose_name = 'Bildirim'
        verbose_name_plural = 'Bildirimler'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.title}"

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Özel kullanıcı modeli - yönetici ve normal kullanıcı ayrımı için
    TC Kimlik Numarası ile giriş yapılır, username email'den otomatik oluşturulur
    """
    
    USER_TYPE_CHOICES = (
        ('user', 'Kullanıcı'),
        ('admin', 'Yönetici'),
    )
    
    user_type = models.CharField(
        max_length=10,
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
        return self.user_type == 'admin'

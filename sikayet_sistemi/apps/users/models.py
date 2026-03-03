from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Kullanıcı profili - User modelini genişletme"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefon Numarası')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Kullanıcı Profili'
        verbose_name_plural = 'Kullanıcı Profilleri'

    def __str__(self):
        return f"{self.user.username} - Profili"


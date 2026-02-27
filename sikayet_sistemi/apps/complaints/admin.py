from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'district', 'priority', 'status', 'created_at')
    list_filter = ('priority', 'status', 'category', 'created_at')
    search_fields = ('title', 'description', 'district', 'city')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Şikayet Başlığı ve Açıklaması', {
            'fields': ('title', 'description')
        }),
        ('Kategori ve Konum', {
            'fields': ('category', 'city', 'district', 'address')
        }),
        ('Durum', {
            'fields': ('priority', 'status')
        }),
        ('Kullanıcı', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
        ('Tarih Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = list(UserAdmin.fieldsets) + [
        (
            "Ek Bilgiler",
            {
                "fields": (
                    "user_type",
                    "phone",
                    "tc_id",
                    "address",
                    "company",
                    "created_at",
                )
            },
        ),
    ]  # type: ignore[assignment]
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "tc_id",
        "phone",
        "user_type",
        "created_at",
    )
    list_filter = ("user_type", "created_at", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "tc_id", "phone")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

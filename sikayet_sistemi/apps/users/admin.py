from typing import Any, Tuple

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets: Tuple[Any, ...] = BaseUserAdmin.fieldsets + (  # type: ignore[assignment]
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
    )
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

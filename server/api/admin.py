from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Ping, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "name", "code_name", "is_active", "is_staff")
    search_fields = ("email", "name", "code_name")
    list_filter = ("is_active", "is_staff")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("name", "code_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "name",
                    "code_name",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    @admin.register(Ping)
    class PingAdmin(admin.ModelAdmin):
        list_display = (
            "id",
            "timestamp",
            "user",
            "latitude",
            "longitude",
            "parent_ping",
        )
        search_fields = ("user",)
        list_filter = ("user", "timestamp")
        ordering = ("-timestamp",)

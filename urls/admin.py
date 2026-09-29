from django.contrib import admin
from .models import URL, ClickEvent


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "original_url",
        "short_code",
        "custom_alias",
        "status",
        "expires_at",
        "created_at",
    )

    search_fields = (
        "original_url",
        "short_code",
        "custom_alias",
    )

    list_filter = (
        "status",
        "created_at",
    )


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "url",
        "timestamp",
        "referrer",
        "device",
        "browser",
        "country",
    )

    list_filter = ("timestamp",)
    search_fields = ("url__short_code", "referrer", "device")
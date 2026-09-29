from celery import shared_task
from django.utils import timezone

from .models import URL


@shared_task
def deactivate_expired_urls():
    expired_urls = URL.objects.filter(
        expires_at__isnull=False,
        expires_at__lte=timezone.now(),
        status=True
    )

    count = expired_urls.update(status=False)

    return f"{count} expired URLs deactivated"
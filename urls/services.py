from .models import URL
from .base62 import encode


def create_short_code(url):
    url.short_code = encode(url.id)
    url.save(update_fields=["short_code"])
    return url.short_code
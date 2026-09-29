from django.urls import path
from .views import (
    create_url,
    redirect_url,
    analytics,
    list_urls,
    url_detail,
    home
)

urlpatterns = [
    path("", home, name="home"),
    path("api/urls", create_url, name="create_url"),
    path("api/urls/all", list_urls, name="list_urls"),
    path("api/urls/<int:url_id>", url_detail, name="url_detail"),
    path("api/urls/<int:url_id>/analytics", analytics, name="analytics"),
    path("<str:short_code>", redirect_url, name="redirect_url"),
]
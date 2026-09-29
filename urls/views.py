from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from .models import URL, ClickEvent
from .services import create_short_code
from django.shortcuts import render
from django.core.cache import cache
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_url(request):
    original_url = request.data.get("original_url")
    custom_alias = request.data.get("custom_alias")
    expires_at = request.data.get("expires_at")

    if not original_url:
        return Response(
            {"error": "original_url is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    validator = URLValidator()

    try:
        validator(original_url)
    except ValidationError:
        return Response(
            {"error": "Invalid URL"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if custom_alias:
        if URL.objects.filter(custom_alias=custom_alias).exists():
            return Response(
                {"error": "Custom alias already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        url = URL.objects.create(
            user=request.user,
            original_url=original_url,
            custom_alias=custom_alias,
            short_code=custom_alias,
            expires_at=expires_at
        )

    else:
        url = URL.objects.create(
            user=request.user,
            original_url=original_url,
            expires_at=expires_at
        )

        create_short_code(url)

    return Response(
        {
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "custom_alias": url.custom_alias
        },
        status=status.HTTP_201_CREATED
    )


def redirect_url(request, short_code):

    cache_key = f"url:{short_code}"

    # Try Redis first
    original_url = cache.get(cache_key)

    # If not in Redis, get it from the database
    if not original_url:

        url = URL.objects.filter(
            short_code=short_code
        ).first()

        if not url:
            url = URL.objects.filter(
                custom_alias=short_code
            ).first()

        if not url:
            return redirect("/")

        # Check whether URL is active
        if not url.status:
            return redirect("/")

        # Check expiration
        if url.expires_at and timezone.now() > url.expires_at:
            return redirect("/")

        original_url = url.original_url

        # Store in Redis for 1 hour
        cache.set(
            cache_key,
            original_url,
            timeout=3600
        )
        
    else:
        # URL was found in Redis
        url = URL.objects.filter(
            short_code=short_code
        ).first()

        if not url:
            url = URL.objects.filter(
                custom_alias=short_code
            ).first()

    # If database record doesn't exist
    if not url:
        cache.delete(cache_key)
        return redirect("/")

    # Check status
    if not url.status:
        cache.delete(cache_key)
        return redirect("/")

    # Check expiration
    if url.expires_at and timezone.now() > url.expires_at:
        cache.delete(cache_key)
        return redirect("/")

    # Record click
    ClickEvent.objects.create(
        url=url,
        referrer=request.META.get("HTTP_REFERER"),
        device=request.META.get("HTTP_USER_AGENT"),
    )

    return redirect(original_url)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics(request, url_id):

    url = get_object_or_404(
        URL,
        id=url_id,
        user=request.user
    )

    total_clicks = ClickEvent.objects.filter(url=url).count()

    return Response({
        "url_id": url.id,
        "short_code": url.short_code,
        "original_url": url.original_url,
        "total_clicks": total_clicks
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_urls(request):
    urls = URL.objects.filter(
        user=request.user
    ).order_by("-created_at")

    data = []

    for url in urls:
        data.append({
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "custom_alias": url.custom_alias,
            "expires_at": url.expires_at,
            "status": url.status,
            "created_at": url.created_at
        })

    return Response(data)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def url_detail(request, url_id):
    url = get_object_or_404(
        URL,
        id=url_id,
        user=request.user
    )

    if request.method == "GET":
        return Response({
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "custom_alias": url.custom_alias,
            "expires_at": url.expires_at,
            "status": url.status,
            "created_at": url.created_at
        })

    if request.method == "PUT":
        original_url = request.data.get("original_url")
        custom_alias = request.data.get("custom_alias")

        if original_url:
            url.original_url = original_url

        if custom_alias:
            existing = URL.objects.filter(
                custom_alias=custom_alias
            ).exclude(id=url.id).exists()

            if existing:
                return Response(
                    {"error": "Custom alias already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            url.custom_alias = custom_alias
            url.short_code = custom_alias

        url.save()

        return Response({
            "message": "URL updated successfully",
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "custom_alias": url.custom_alias
        })

    if request.method == "DELETE":
        url.delete()

        return Response(
            {"message": "URL deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

def home(request):
    return render(request, "index.html")
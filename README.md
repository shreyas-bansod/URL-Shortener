# URL Shortener

A URL Shortener web application built with Python, Django REST Framework, Redis, Celery, and SQLite.

## Features

- Shorten long URLs using Base62 encoding
- Custom URL aliases
- URL expiration
- JWT authentication
- Click tracking
- Redis caching
- Celery background task for expired URLs
- REST API
- Django admin dashboard
- Basic URL validation
- Responsive web interface
- API rate limiting

## Technologies Used

- Python
- Django
- Django REST Framework
- SQLite
- Redis / Memurai
- Celery
- JWT Authentication
- HTML, CSS, JavaScript

## Project Structure

```text
URL-Shortener/
│
├── config/
│   ├── celery.py
│   ├── settings.py
│   └── urls.py
│
├── urls/
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── base62.py
│   ├── models.py
│   ├── services.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md


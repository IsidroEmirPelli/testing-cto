"""
ASGI config for News Scraping project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.infrastructure.config.django_settings')

application = get_asgi_application()

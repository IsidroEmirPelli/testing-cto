"""
WSGI config for News Scraping project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.infrastructure.config.django_settings')

application = get_wsgi_application()

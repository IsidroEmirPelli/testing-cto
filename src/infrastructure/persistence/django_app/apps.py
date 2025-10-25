from django.apps import AppConfig


class DjangoPersistenceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.infrastructure.persistence.django_app"
    label = "persistence"
    verbose_name = "News Scraping Persistence"

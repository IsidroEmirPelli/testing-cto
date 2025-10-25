"""
URL Configuration for News Scraping API.
"""

from django.contrib import admin
from django.urls import path
from .views import (
    NewsArticleListCreateView,
    SourceListCreateView,
    UserListCreateView,
    HealthCheckView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("api/articles/", NewsArticleListCreateView.as_view(), name="articles"),
    path("api/sources/", SourceListCreateView.as_view(), name="sources"),
    path("api/users/", UserListCreateView.as_view(), name="users"),
]

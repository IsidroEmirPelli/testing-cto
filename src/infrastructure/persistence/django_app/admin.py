from django.contrib import admin
from .models import UserModel, SourceModel, NewsArticleModel, ScrapingJobModel


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["email", "name"]
    readonly_fields = ["id", "created_at"]


@admin.register(SourceModel)
class SourceAdmin(admin.ModelAdmin):
    list_display = ["get_nombre", "get_dominio", "activo", "created_at"]
    list_filter = ["activo", "source_type", "created_at"]
    search_fields = ["source_type"]
    readonly_fields = ["id", "created_at"]

    def get_nombre(self, obj):
        from src.domain.enums import NewsSource

        return NewsSource(obj.source_type).nombre

    get_nombre.short_description = "Nombre"

    def get_dominio(self, obj):
        from src.domain.enums import NewsSource

        return NewsSource(obj.source_type).dominio

    get_dominio.short_description = "Dominio"


@admin.register(NewsArticleModel)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ["titulo", "fuente", "categoria", "procesado", "fecha_publicacion"]
    list_filter = ["procesado", "fuente", "categoria", "fecha_publicacion"]
    search_fields = ["titulo", "contenido", "fuente", "url"]
    readonly_fields = ["id", "created_at"]
    date_hierarchy = "fecha_publicacion"


@admin.register(ScrapingJobModel)
class ScrapingJobAdmin(admin.ModelAdmin):
    list_display = ["fuente", "status", "total_articulos", "fecha_inicio", "fecha_fin"]
    list_filter = ["status", "fuente", "fecha_inicio"]
    search_fields = ["fuente"]
    readonly_fields = ["id", "created_at"]
    date_hierarchy = "fecha_inicio"

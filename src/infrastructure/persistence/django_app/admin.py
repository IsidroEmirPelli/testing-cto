from django.contrib import admin
from .models import UserModel, SourceModel, NewsArticleModel, ScrapingJobModel


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email', 'name']
    readonly_fields = ['id', 'created_at']


@admin.register(SourceModel)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'dominio', 'pais', 'activo', 'created_at']
    list_filter = ['activo', 'pais', 'created_at']
    search_fields = ['nombre', 'dominio']
    readonly_fields = ['id', 'created_at']


@admin.register(NewsArticleModel)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fuente', 'categoria', 'procesado', 'fecha_publicacion']
    list_filter = ['procesado', 'fuente', 'categoria', 'fecha_publicacion']
    search_fields = ['titulo', 'contenido', 'fuente', 'url']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'fecha_publicacion'


@admin.register(ScrapingJobModel)
class ScrapingJobAdmin(admin.ModelAdmin):
    list_display = ['fuente', 'status', 'total_articulos', 'fecha_inicio', 'fecha_fin']
    list_filter = ['status', 'fuente', 'fecha_inicio']
    search_fields = ['fuente']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'fecha_inicio'

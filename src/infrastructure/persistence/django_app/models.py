"""
Django models - Adaptadores de persistencia para la arquitectura hexagonal.
Estos modelos NO son las entidades del dominio, son adaptadores de infraestructura.
"""
import uuid
from django.db import models


class UserModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"


class SourceModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    dominio = models.CharField(max_length=255, unique=True)
    pais = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sources'
        verbose_name = 'Source'
        verbose_name_plural = 'Sources'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dominio']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.dominio})"


class NewsArticleModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=500)
    contenido = models.TextField()
    fuente = models.CharField(max_length=255, db_index=True)
    fecha_publicacion = models.DateTimeField()
    url = models.URLField(max_length=1000, unique=True)
    categoria = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    procesado = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'news_articles'
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'
        ordering = ['-fecha_publicacion']
        indexes = [
            models.Index(fields=['fuente', 'fecha_publicacion']),
            models.Index(fields=['categoria']),
            models.Index(fields=['procesado']),
        ]

    def __str__(self):
        return self.titulo


class ScrapingJobModel(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fuente = models.CharField(max_length=255, db_index=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    total_articulos = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'scraping_jobs'
        verbose_name = 'Scraping Job'
        verbose_name_plural = 'Scraping Jobs'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['fuente', 'status']),
            models.Index(fields=['status', 'fecha_inicio']),
        ]

    def __str__(self):
        return f"Job {self.fuente} - {self.status}"

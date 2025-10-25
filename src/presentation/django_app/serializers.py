"""
Django REST Framework Serializers.
Capa de presentación - validan y serializan datos de entrada/salida.
"""
from rest_framework import serializers


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=255)


class UserUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField()
    name = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)


class SourceCreateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=255)
    dominio = serializers.CharField(max_length=255)
    pais = serializers.CharField(max_length=100)


class SourceUpdateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=255, required=False)
    dominio = serializers.CharField(max_length=255, required=False)
    pais = serializers.CharField(max_length=100, required=False)


class SourceSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    nombre = serializers.CharField()
    dominio = serializers.CharField()
    pais = serializers.CharField()
    activo = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)


class NewsArticleCreateSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=500)
    contenido = serializers.CharField()
    fuente = serializers.CharField(max_length=255)
    fecha_publicacion = serializers.DateTimeField()
    url = serializers.URLField()
    categoria = serializers.CharField(max_length=255, required=False, allow_null=True)


class NewsArticleUpdateSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=500, required=False)
    contenido = serializers.CharField(required=False)
    categoria = serializers.CharField(max_length=255, required=False, allow_null=True)


class NewsArticleSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    titulo = serializers.CharField()
    contenido = serializers.CharField()
    fuente = serializers.CharField()
    fecha_publicacion = serializers.DateTimeField()
    url = serializers.URLField()
    categoria = serializers.CharField(allow_null=True)
    procesado = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)


class ScrapingJobCreateSerializer(serializers.Serializer):
    fuente = serializers.CharField(max_length=255)


class ScrapingJobSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    fuente = serializers.CharField()
    fecha_inicio = serializers.DateTimeField()
    fecha_fin = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()
    total_articulos = serializers.IntegerField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)

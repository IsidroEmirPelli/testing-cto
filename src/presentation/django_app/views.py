"""
Django REST Framework Views.
Capa de presentación - orquesta llamadas a casos de uso.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import async_to_sync

from src.application.dto import (
    CreateNewsArticleDTO,
    CreateSourceDTO,
    CreateUserDTO,
)
from src.application.use_cases import (
    CreateArticleUseCase,
    ListArticlesUseCase,
    RegisterSourceUseCase,
    CreateUserUseCase,
    ListUsersUseCase,
)
from src.domain.enums import NewsSource
from src.infrastructure.persistence.django_repositories import (
    DjangoNewsArticleRepository,
    DjangoSourceRepository,
    DjangoUserRepository,
)
from .serializers import (
    NewsArticleCreateSerializer,
    NewsArticleSerializer,
    SourceCreateSerializer,
    SourceSerializer,
    UserCreateSerializer,
    UserSerializer,
)


class NewsArticleListCreateView(APIView):
    """Vista para listar y crear artículos de noticias"""

    def get(self, request):
        skip = int(request.GET.get("skip", 0))
        limit = int(request.GET.get("limit", 100))

        use_case = ListArticlesUseCase(DjangoNewsArticleRepository())
        articles = async_to_sync(use_case.execute)(skip=skip, limit=limit)

        serializer = NewsArticleSerializer(
            [
                {
                    "id": article.id,
                    "titulo": article.titulo,
                    "contenido": article.contenido,
                    "fuente": article.fuente,
                    "fecha_publicacion": article.fecha_publicacion,
                    "url": article.url,
                    "categoria": article.categoria,
                    "procesado": article.procesado,
                    "created_at": article.created_at,
                    "updated_at": article.updated_at,
                }
                for article in articles
            ],
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = NewsArticleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = CreateNewsArticleDTO(**serializer.validated_data)
        use_case = CreateArticleUseCase(DjangoNewsArticleRepository())

        try:
            article = async_to_sync(use_case.execute)(dto)
            response_serializer = NewsArticleSerializer(
                {
                    "id": article.id,
                    "titulo": article.titulo,
                    "contenido": article.contenido,
                    "fuente": article.fuente,
                    "fecha_publicacion": article.fecha_publicacion,
                    "url": article.url,
                    "categoria": article.categoria,
                    "procesado": article.procesado,
                    "created_at": article.created_at,
                    "updated_at": article.updated_at,
                }
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SourceListCreateView(APIView):
    """Vista para listar y registrar fuentes"""

    def post(self, request):
        serializer = SourceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        source_type_str = serializer.validated_data["source_type"]
        source_type = NewsSource[source_type_str]

        dto = CreateSourceDTO(source_type=source_type)
        use_case = RegisterSourceUseCase(DjangoSourceRepository())

        try:
            source = async_to_sync(use_case.execute)(dto)
            response_serializer = SourceSerializer(
                {
                    "id": source.id,
                    "source_type": source.source_type.name,
                    "nombre": source.nombre,
                    "dominio": source.dominio,
                    "pais": source.pais,
                    "activo": source.activo,
                    "created_at": source.created_at,
                    "updated_at": source.updated_at,
                }
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserListCreateView(APIView):
    """Vista para listar y crear usuarios"""

    def get(self, request):
        skip = int(request.GET.get("skip", 0))
        limit = int(request.GET.get("limit", 100))

        use_case = ListUsersUseCase(DjangoUserRepository())
        users = async_to_sync(use_case.execute)(skip=skip, limit=limit)

        serializer = UserSerializer(
            [
                {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                }
                for user in users
            ],
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = CreateUserDTO(**serializer.validated_data)
        use_case = CreateUserUseCase(DjangoUserRepository())

        try:
            user = async_to_sync(use_case.execute)(dto)
            response_serializer = UserSerializer(
                {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                }
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class HealthCheckView(APIView):
    """Vista para health check"""

    def get(self, request):
        return Response(
            {
                "status": "healthy",
                "service": "News Scraping API",
                "architecture": "Hexagonal (Clean Architecture)",
            }
        )

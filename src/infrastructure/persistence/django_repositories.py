"""
Implementaciones Django de los repositorios.
Adaptadores que conectan las entidades del dominio con Django ORM.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.domain.entities import NewsArticle, Source, ScrapingJob, User
from src.domain.enums import NewsSource
from src.domain.repositories import (
    NewsArticleRepository,
    SourceRepository,
    ScrapingJobRepository,
    UserRepository,
)
from src.infrastructure.persistence.django_app.models import (
    NewsArticleModel,
    SourceModel,
    ScrapingJobModel,
    UserModel,
)


class DjangoUserRepository(UserRepository):
    """Adaptador Django para UserRepository"""

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            name=model.name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            name=entity.name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        await model.asave()
        return self._to_entity(model)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        try:
            model = await UserModel.objects.aget(id=user_id)
            return self._to_entity(model)
        except UserModel.DoesNotExist:
            return None

    async def get_by_email(self, email: str) -> Optional[User]:
        try:
            model = await UserModel.objects.aget(email=email)
            return self._to_entity(model)
        except UserModel.DoesNotExist:
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        models = [model async for model in UserModel.objects.all()[skip : skip + limit]]
        return [self._to_entity(model) for model in models]

    async def update(self, user: User) -> User:
        model = await UserModel.objects.aget(id=user.id)
        model.email = user.email
        model.name = user.name
        model.is_active = user.is_active
        model.updated_at = user.updated_at
        await model.asave()
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        try:
            model = await UserModel.objects.aget(id=user_id)
            await model.adelete()
            return True
        except UserModel.DoesNotExist:
            return False


class DjangoSourceRepository(SourceRepository):
    """Adaptador Django para SourceRepository"""

    @staticmethod
    def _to_entity(model: SourceModel) -> Source:
        source_type = NewsSource(model.source_type)
        return Source(
            id=model.id,
            source_type=source_type,
            activo=model.activo,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: Source) -> SourceModel:
        return SourceModel(
            id=entity.id,
            source_type=entity.source_type.value,
            activo=entity.activo,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, source: Source) -> Source:
        model = self._to_model(source)
        await model.asave()
        return self._to_entity(model)

    async def get_by_id(self, source_id: UUID) -> Optional[Source]:
        try:
            model = await SourceModel.objects.aget(id=source_id)
            return self._to_entity(model)
        except SourceModel.DoesNotExist:
            return None

    async def get_by_nombre(self, nombre: str) -> Optional[Source]:
        try:
            source_type = NewsSource.from_nombre(nombre)
            model = await SourceModel.objects.aget(source_type=source_type.value)
            return self._to_entity(model)
        except (SourceModel.DoesNotExist, ValueError):
            return None

    async def get_by_dominio(self, dominio: str) -> Optional[Source]:
        try:
            source_type = NewsSource.from_dominio(dominio)
            model = await SourceModel.objects.aget(source_type=source_type.value)
            return self._to_entity(model)
        except (SourceModel.DoesNotExist, ValueError):
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Source]:
        models = [
            model async for model in SourceModel.objects.all()[skip : skip + limit]
        ]
        return [self._to_entity(model) for model in models]

    async def get_active_sources(self, skip: int = 0, limit: int = 100) -> List[Source]:
        models = [
            model
            async for model in SourceModel.objects.filter(activo=True)[
                skip : skip + limit
            ]
        ]
        return [self._to_entity(model) for model in models]

    async def update(self, source: Source) -> Source:
        model = await SourceModel.objects.aget(id=source.id)
        model.source_type = source.source_type.value
        model.activo = source.activo
        model.updated_at = source.updated_at
        await model.asave()
        return self._to_entity(model)

    async def delete(self, source_id: UUID) -> bool:
        try:
            model = await SourceModel.objects.aget(id=source_id)
            await model.adelete()
            return True
        except SourceModel.DoesNotExist:
            return False


class DjangoNewsArticleRepository(NewsArticleRepository):
    """Adaptador Django para NewsArticleRepository"""

    @staticmethod
    def _to_entity(model: NewsArticleModel) -> NewsArticle:
        return NewsArticle(
            id=model.id,
            titulo=model.titulo,
            contenido=model.contenido,
            fuente=model.fuente,
            fecha_publicacion=model.fecha_publicacion,
            url=model.url,
            categoria=model.categoria,
            procesado=model.procesado,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: NewsArticle) -> NewsArticleModel:
        return NewsArticleModel(
            id=entity.id,
            titulo=entity.titulo,
            contenido=entity.contenido,
            fuente=entity.fuente,
            fecha_publicacion=entity.fecha_publicacion,
            url=entity.url,
            categoria=entity.categoria,
            procesado=entity.procesado,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, article: NewsArticle) -> NewsArticle:
        model = self._to_model(article)
        await model.asave()
        return self._to_entity(model)

    async def get_by_id(self, article_id: UUID) -> Optional[NewsArticle]:
        try:
            model = await NewsArticleModel.objects.aget(id=article_id)
            return self._to_entity(model)
        except NewsArticleModel.DoesNotExist:
            return None

    async def get_by_url(self, url: str) -> Optional[NewsArticle]:
        try:
            model = await NewsArticleModel.objects.aget(url=url)
            return self._to_entity(model)
        except NewsArticleModel.DoesNotExist:
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[NewsArticle]:
        models = [
            model async for model in NewsArticleModel.objects.all()[skip : skip + limit]
        ]
        return [self._to_entity(model) for model in models]

    async def get_by_fuente(
        self, fuente: str, skip: int = 0, limit: int = 100
    ) -> List[NewsArticle]:
        models = [
            model
            async for model in NewsArticleModel.objects.filter(fuente=fuente)[
                skip : skip + limit
            ]
        ]
        return [self._to_entity(model) for model in models]

    async def get_by_categoria(
        self, categoria: str, skip: int = 0, limit: int = 100
    ) -> List[NewsArticle]:
        models = [
            model
            async for model in NewsArticleModel.objects.filter(categoria=categoria)[
                skip : skip + limit
            ]
        ]
        return [self._to_entity(model) for model in models]

    async def update(self, article: NewsArticle) -> NewsArticle:
        model = await NewsArticleModel.objects.aget(id=article.id)
        model.titulo = article.titulo
        model.contenido = article.contenido
        model.fuente = article.fuente
        model.fecha_publicacion = article.fecha_publicacion
        model.url = article.url
        model.categoria = article.categoria
        model.procesado = article.procesado
        model.updated_at = article.updated_at
        await model.asave()
        return self._to_entity(model)

    async def delete(self, article_id: UUID) -> bool:
        try:
            model = await NewsArticleModel.objects.aget(id=article_id)
            await model.adelete()
            return True
        except NewsArticleModel.DoesNotExist:
            return False


class DjangoScrapingJobRepository(ScrapingJobRepository):
    """Adaptador Django para ScrapingJobRepository"""

    @staticmethod
    def _to_entity(model: ScrapingJobModel) -> ScrapingJob:
        return ScrapingJob(
            id=model.id,
            fuente=model.fuente,
            fecha_inicio=model.fecha_inicio,
            fecha_fin=model.fecha_fin,
            status=model.status,
            total_articulos=model.total_articulos,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: ScrapingJob) -> ScrapingJobModel:
        return ScrapingJobModel(
            id=entity.id,
            fuente=entity.fuente,
            fecha_inicio=entity.fecha_inicio,
            fecha_fin=entity.fecha_fin,
            status=entity.status,
            total_articulos=entity.total_articulos,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, job: ScrapingJob) -> ScrapingJob:
        model = self._to_model(job)
        await model.asave()
        return self._to_entity(model)

    async def get_by_id(self, job_id: UUID) -> Optional[ScrapingJob]:
        try:
            model = await ScrapingJobModel.objects.aget(id=job_id)
            return self._to_entity(model)
        except ScrapingJobModel.DoesNotExist:
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ScrapingJob]:
        models = [
            model async for model in ScrapingJobModel.objects.all()[skip : skip + limit]
        ]
        return [self._to_entity(model) for model in models]

    async def get_by_fuente(
        self, fuente: str, skip: int = 0, limit: int = 100
    ) -> List[ScrapingJob]:
        models = [
            model
            async for model in ScrapingJobModel.objects.filter(fuente=fuente)[
                skip : skip + limit
            ]
        ]
        return [self._to_entity(model) for model in models]

    async def get_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> List[ScrapingJob]:
        models = [
            model
            async for model in ScrapingJobModel.objects.filter(status=status)[
                skip : skip + limit
            ]
        ]
        return [self._to_entity(model) for model in models]

    async def update(self, job: ScrapingJob) -> ScrapingJob:
        model = await ScrapingJobModel.objects.aget(id=job.id)
        model.fuente = job.fuente
        model.fecha_inicio = job.fecha_inicio
        model.fecha_fin = job.fecha_fin
        model.status = job.status
        model.total_articulos = job.total_articulos
        model.updated_at = job.updated_at
        await model.asave()
        return self._to_entity(model)

    async def delete(self, job_id: UUID) -> bool:
        try:
            model = await ScrapingJobModel.objects.aget(id=job_id)
            await model.adelete()
            return True
        except ScrapingJobModel.DoesNotExist:
            return False

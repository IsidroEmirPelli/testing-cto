from src.application.dto.news_article_dto import (
    CreateNewsArticleDTO,
    NewsArticleDTO,
)
from src.domain.entities.news_article import NewsArticle
from src.domain.repositories.news_article_repository import NewsArticleRepository


class CreateArticleUseCase:

    def __init__(self, article_repository: NewsArticleRepository):
        self._article_repository = article_repository

    async def execute(self, dto: CreateNewsArticleDTO) -> NewsArticleDTO:
        existing_article = await self._article_repository.get_by_url(dto.url)
        if existing_article:
            raise ValueError(f"Article with URL {dto.url} already exists")

        article = NewsArticle.create(
            titulo=dto.titulo,
            contenido=dto.contenido,
            fuente=dto.fuente,
            fecha_publicacion=dto.fecha_publicacion,
            url=dto.url,
            categoria=dto.categoria,
        )
        created_article = await self._article_repository.create(article)

        return self._to_dto(created_article)

    @staticmethod
    def _to_dto(article: NewsArticle) -> NewsArticleDTO:
        return NewsArticleDTO(
            id=article.id,
            titulo=article.titulo,
            contenido=article.contenido,
            fuente=article.fuente,
            fecha_publicacion=article.fecha_publicacion,
            url=article.url,
            categoria=article.categoria,
            procesado=article.procesado,
            created_at=article.created_at,
            updated_at=article.updated_at,
        )

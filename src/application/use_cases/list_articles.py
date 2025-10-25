from typing import List

from src.application.dto.news_article_dto import NewsArticleDTO
from src.domain.entities.news_article import NewsArticle
from src.domain.repositories.news_article_repository import NewsArticleRepository


class ListArticlesUseCase:

    def __init__(self, article_repository: NewsArticleRepository):
        self._article_repository = article_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[NewsArticleDTO]:
        articles = await self._article_repository.get_all(skip=skip, limit=limit)
        return [self._to_dto(article) for article in articles]

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

import logging
from typing import List
from src.domain.entities.news_article import NewsArticle

logger = logging.getLogger(__name__)


class MockQueue:
    def __init__(self):
        self._queue: List[NewsArticle] = []
        logger.info("MockQueue inicializada")

    def enqueue(self, article: NewsArticle) -> None:
        self._queue.append(article)
        logger.info(
            f"Artículo encolado: {article.titulo[:50]}... - Fuente: {article.fuente}"
        )

    def enqueue_batch(self, articles: List[NewsArticle]) -> None:
        for article in articles:
            self.enqueue(article)
        logger.info(f"Batch de {len(articles)} artículos encolados")

    def dequeue(self) -> NewsArticle:
        if not self._queue:
            logger.warning("Intento de desencolar de queue vacía")
            return None
        article = self._queue.pop(0)
        logger.info(f"Artículo desencolado: {article.titulo[:50]}...")
        return article

    def size(self) -> int:
        return len(self._queue)

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def clear(self) -> None:
        count = len(self._queue)
        self._queue.clear()
        logger.info(f"Queue limpiada - {count} artículos eliminados")

    def get_all(self) -> List[NewsArticle]:
        return self._queue.copy()

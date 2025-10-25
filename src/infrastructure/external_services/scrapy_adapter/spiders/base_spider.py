import scrapy
import logging
from datetime import datetime, timezone
from typing import Optional
from src.infrastructure.external_services.scrapy_adapter.items import NewsArticleItem

logger = logging.getLogger(__name__)


class BaseNewsSpider(scrapy.Spider):
    max_articles = 15
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.articles_count = 0
    
    def create_article_item(
        self,
        titulo: str,
        contenido: str,
        fuente: str,
        url: str,
        fecha_publicacion: Optional[datetime] = None,
        categoria: Optional[str] = None
    ) -> NewsArticleItem:
        if self.articles_count >= self.max_articles:
            logger.info(f"Límite de artículos alcanzado para {fuente}: {self.max_articles}")
            return None
        
        self.articles_count += 1
        
        item = NewsArticleItem()
        item['titulo'] = titulo
        item['contenido'] = contenido
        item['fuente'] = fuente
        item['url'] = url
        item['fecha_publicacion'] = fecha_publicacion or datetime.now(timezone.utc)
        item['categoria'] = categoria
        
        return item
    
    def handle_error(self, failure):
        logger.error(f"Error en spider {self.name}: {failure.value}")

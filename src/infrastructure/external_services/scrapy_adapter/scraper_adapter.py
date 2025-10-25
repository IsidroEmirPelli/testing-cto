import logging
from typing import List
from datetime import datetime, timezone
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from src.domain.ports.scraper_port import IScraperPort
from src.domain.entities.news_article import NewsArticle
from src.infrastructure.external_services.mock_queue import MockQueue
from .spiders.clarin_spider import ClarinSpider
from .spiders.lanacion_spider import LaNacionSpider
from .spiders.infobae_spider import InfobaeSpider
from .spiders.pagina12_spider import Pagina12Spider

logger = logging.getLogger(__name__)


class ScrapyAdapter(IScraperPort):
    SPIDER_MAP = {
        "clarin": ClarinSpider,
        "lanacion": LaNacionSpider,
        "infobae": InfobaeSpider,
        "pagina12": Pagina12Spider,
    }

    def __init__(self, queue: MockQueue = None):
        self.queue = queue or MockQueue()
        self.scraped_articles: List[NewsArticle] = []
        logger.info("ScrapyAdapter inicializado")

    def scrape_sources(self, sources: List[str]) -> List[NewsArticle]:
        logger.info(f"Iniciando scraping de {len(sources)} fuentes: {sources}")

        self.scraped_articles = []

        try:
            from scrapy import signals
            from scrapy.signalmanager import dispatcher

            def spider_closed(spider):
                logger.info(f"Spider {spider.name} cerrado")

            def item_scraped(item, response, spider):
                try:
                    article = NewsArticle.create(
                        titulo=item["titulo"],
                        contenido=item["contenido"],
                        fuente=item["fuente"],
                        fecha_publicacion=item["fecha_publicacion"],
                        url=item["url"],
                        categoria=item.get("categoria"),
                    )
                    self.scraped_articles.append(article)
                    self.queue.enqueue(article)
                    logger.info(
                        f"Artículo procesado: {article.titulo[:50]}... - Fuente: {article.fuente}"
                    )
                except Exception as e:
                    logger.error(f"Error al procesar item: {e}")

            dispatcher.connect(spider_closed, signal=signals.spider_closed)
            dispatcher.connect(item_scraped, signal=signals.item_scraped)

            settings = self._get_scrapy_settings()
            process = CrawlerProcess(settings)

            for source in sources:
                source_lower = source.lower().replace(" ", "").replace("/", "")
                spider_class = self.SPIDER_MAP.get(source_lower)

                if spider_class:
                    logger.info(f"Añadiendo spider: {spider_class.name}")
                    process.crawl(spider_class)
                else:
                    logger.warning(f"Spider no encontrado para fuente: {source}")

            if not process.crawlers:
                logger.warning("No se encontraron spiders válidos para ejecutar")
                return []

            process.start()

            logger.info(
                f"Scraping completado. Total artículos: {len(self.scraped_articles)}"
            )
            return self.scraped_articles

        except Exception as e:
            logger.error(f"Error en scraping: {e}", exc_info=True)
            return self.scraped_articles

    def _get_scrapy_settings(self):
        from .settings import (
            BOT_NAME,
            ROBOTSTXT_OBEY,
            CONCURRENT_REQUESTS,
            DOWNLOAD_DELAY,
            CONCURRENT_REQUESTS_PER_DOMAIN,
            COOKIES_ENABLED,
            DEFAULT_REQUEST_HEADERS,
            ITEM_PIPELINES,
            AUTOTHROTTLE_ENABLED,
            AUTOTHROTTLE_START_DELAY,
            AUTOTHROTTLE_MAX_DELAY,
            AUTOTHROTTLE_TARGET_CONCURRENCY,
            LOG_LEVEL,
            RETRY_TIMES,
            RETRY_HTTP_CODES,
            DOWNLOAD_TIMEOUT,
        )

        settings = {
            "BOT_NAME": BOT_NAME,
            "ROBOTSTXT_OBEY": ROBOTSTXT_OBEY,
            "CONCURRENT_REQUESTS": CONCURRENT_REQUESTS,
            "DOWNLOAD_DELAY": DOWNLOAD_DELAY,
            "CONCURRENT_REQUESTS_PER_DOMAIN": CONCURRENT_REQUESTS_PER_DOMAIN,
            "COOKIES_ENABLED": COOKIES_ENABLED,
            "DEFAULT_REQUEST_HEADERS": DEFAULT_REQUEST_HEADERS,
            "ITEM_PIPELINES": ITEM_PIPELINES,
            "AUTOTHROTTLE_ENABLED": AUTOTHROTTLE_ENABLED,
            "AUTOTHROTTLE_START_DELAY": AUTOTHROTTLE_START_DELAY,
            "AUTOTHROTTLE_MAX_DELAY": AUTOTHROTTLE_MAX_DELAY,
            "AUTOTHROTTLE_TARGET_CONCURRENCY": AUTOTHROTTLE_TARGET_CONCURRENCY,
            "LOG_LEVEL": LOG_LEVEL,
            "RETRY_TIMES": RETRY_TIMES,
            "RETRY_HTTP_CODES": RETRY_HTTP_CODES,
            "DOWNLOAD_TIMEOUT": DOWNLOAD_TIMEOUT,
        }

        return settings

    def get_queue(self) -> MockQueue:
        return self.queue

import scrapy
import logging
from datetime import datetime, timezone
from .base_spider import BaseNewsSpider

logger = logging.getLogger(__name__)


class LaNacionSpider(BaseNewsSpider):
    name = "lanacion"
    allowed_domains = ["lanacion.com.ar"]
    start_urls = [
        "https://www.lanacion.com.ar/",
        "https://www.lanacion.com.ar/politica/",
        "https://www.lanacion.com.ar/economia/",
    ]

    custom_settings = {"CLOSESPIDER_ITEMCOUNT": 15}

    def parse(self, response):
        try:
            article_links = response.css(
                "article a::attr(href), h2 a::attr(href), h3 a::attr(href)"
            ).getall()
            article_links = list(set(article_links))[:15]

            for link in article_links:
                if self.articles_count >= self.max_articles:
                    break

                if link.startswith("/"):
                    link = response.urljoin(link)

                if "/tema/" in link or "/autor/" in link or "/seccion/" in link:
                    continue

                if not link.startswith("https://www.lanacion.com.ar/"):
                    continue

                yield scrapy.Request(
                    link,
                    callback=self.parse_article,
                    errback=self.handle_error,
                    dont_filter=True,
                )

        except Exception as e:
            logger.error(f"Error en parse de La Nación: {e}")

    def parse_article(self, response):
        try:
            if self.articles_count >= self.max_articles:
                return

            titulo = response.css("h1.com-title::text, h1::text").get()

            if not titulo:
                logger.warning(f"No se encontró título en {response.url}")
                return

            paragraphs = response.css(
                "div.nota p::text, article p::text, div.contenido p::text"
            ).getall()
            contenido = " ".join(paragraphs)

            if not contenido:
                contenido_div = response.css("div.nota, article, div.contenido").get()
                if contenido_div:
                    contenido = contenido_div

            categoria = response.css(
                "div.com-breadcrumb a::text, nav.breadcrumb a::text"
            ).getall()
            categoria_str = categoria[1] if len(categoria) > 1 else None

            item = self.create_article_item(
                titulo=titulo.strip() if titulo else "",
                contenido=contenido,
                fuente="La Nación",
                url=response.url,
                fecha_publicacion=datetime.now(timezone.utc),
                categoria=categoria_str,
            )

            if item:
                yield item

        except Exception as e:
            logger.error(f"Error parseando artículo de La Nación {response.url}: {e}")

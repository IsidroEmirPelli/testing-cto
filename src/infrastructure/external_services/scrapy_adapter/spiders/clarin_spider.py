import scrapy
import logging
from datetime import datetime, timezone
from .base_spider import BaseNewsSpider

logger = logging.getLogger(__name__)


class ClarinSpider(BaseNewsSpider):
    name = "clarin"
    allowed_domains = ["clarin.com"]
    start_urls = [
        "https://www.clarin.com/ultimas-noticias/",
        "https://www.clarin.com/politica/",
        "https://www.clarin.com/economia/",
    ]

    custom_settings = {"CLOSESPIDER_ITEMCOUNT": 15}

    def parse(self, response):
        try:
            article_links = response.css("article a::attr(href)").getall()
            article_links = list(set(article_links))[:15]

            for link in article_links:
                if self.articles_count >= self.max_articles:
                    break

                if link.startswith("/"):
                    link = response.urljoin(link)

                if "/tema/" in link or "/tags/" in link:
                    continue

                yield scrapy.Request(
                    link,
                    callback=self.parse_article,
                    errback=self.handle_error,
                    dont_filter=True,
                )

        except Exception as e:
            logger.error(f"Error en parse de Clarín: {e}")

    def parse_article(self, response):
        try:
            if self.articles_count >= self.max_articles:
                return

            titulo = response.css("h1.title::text, h1.com-title::text").get()
            if not titulo:
                titulo = response.css("h1::text").get()

            if not titulo:
                logger.warning(f"No se encontró título en {response.url}")
                return

            paragraphs = response.css(
                "div.body-nota p::text, div.StyledParagraph p::text, article p::text"
            ).getall()
            contenido = " ".join(paragraphs)

            if not contenido:
                contenido_div = response.css(
                    "div.body-nota, div.StyledParagraph, article"
                ).get()
                if contenido_div:
                    contenido = contenido_div

            categoria = response.css(
                "div.breadcrumb a::text, nav.breadcrumb a::text"
            ).getall()
            categoria_str = categoria[1] if len(categoria) > 1 else None

            item = self.create_article_item(
                titulo=titulo.strip() if titulo else "",
                contenido=contenido,
                fuente="Clarín",
                url=response.url,
                fecha_publicacion=datetime.now(timezone.utc),
                categoria=categoria_str,
            )

            if item:
                yield item

        except Exception as e:
            logger.error(f"Error parseando artículo de Clarín {response.url}: {e}")

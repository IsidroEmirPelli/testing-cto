#!/usr/bin/env python3
import logging
import sys
from src.infrastructure.external_services.scrapy_adapter import ScrapyAdapter
from src.infrastructure.external_services.mock_queue import MockQueue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main():
    logger.info("=== Test Manual del Scraper ===")

    queue = MockQueue()
    scraper = ScrapyAdapter(queue)

    sources = ["clarin", "lanacion", "infobae", "pagina12"]

    logger.info(f"Iniciando scraping de fuentes: {sources}")

    try:
        articles = scraper.scrape_sources(sources)

        logger.info("\n" + "=" * 80)
        logger.info("RESUMEN DEL SCRAPING")
        logger.info("=" * 80)
        logger.info(f"Total de artículos extraídos: {len(articles)}")

        sources_count = {}
        for article in articles:
            sources_count[article.fuente] = sources_count.get(article.fuente, 0) + 1

        logger.info("\nArtículos por fuente:")
        for fuente, count in sources_count.items():
            logger.info(f"  {fuente}: {count} artículos")
            if count >= 10:
                logger.info(f"    ✅ Criterio cumplido (>= 10 artículos)")
            else:
                logger.warning(f"    ⚠️  Criterio no cumplido (< 10 artículos)")

        logger.info(f"\nArtículos en queue: {queue.size()}")

        logger.info("\n" + "=" * 80)
        logger.info("MUESTRA DE ARTÍCULOS EXTRAÍDOS")
        logger.info("=" * 80)

        for i, article in enumerate(articles[:5], 1):
            logger.info(f"\nArtículo #{i}:")
            logger.info(f"  Título: {article.titulo}")
            logger.info(f"  Fuente: {article.fuente}")
            logger.info(f"  URL: {article.url}")
            logger.info(f"  Categoría: {article.categoria}")
            logger.info(f"  Fecha: {article.fecha_publicacion}")
            logger.info(
                f"  Contenido (primeros 200 chars): {article.contenido[:200]}..."
            )
            logger.info(f"  Longitud contenido: {len(article.contenido)} caracteres")

        logger.info("\n" + "=" * 80)
        logger.info("TEST COMPLETADO")
        logger.info("=" * 80)

        if len(articles) >= 10 and all(count >= 10 for count in sources_count.values()):
            logger.info("✅ TODOS LOS CRITERIOS DE ACEPTACIÓN CUMPLIDOS")
            return 0
        else:
            logger.warning("⚠️  ALGUNOS CRITERIOS NO FUERON CUMPLIDOS")
            return 1

    except Exception as e:
        logger.error(f"Error durante el test: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

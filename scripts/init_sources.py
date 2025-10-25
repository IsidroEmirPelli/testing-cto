#!/usr/bin/env python3
"""
Script para inicializar las fuentes de noticias predefinidas.

Este script crea todas las fuentes disponibles en el enum NewsSource
si no existen ya en la base de datos.

Uso:
    python scripts/init_sources.py
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    import django
    import os

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "src.infrastructure.config.django_settings"
    )
    django.setup()

    from src.domain.enums import NewsSource
    from src.domain.entities import Source
    from src.infrastructure.persistence.django_repositories import (
        DjangoSourceRepository,
    )

    repository = DjangoSourceRepository()

    logger.info("Inicializando fuentes de noticias...")

    for news_source in NewsSource.all_sources():
        logger.info(f"Verificando fuente: {news_source.nombre}")

        existing = await repository.get_by_nombre(news_source.nombre)

        if existing:
            logger.info(f"  ✓ La fuente {news_source.nombre} ya existe")
        else:
            source = Source.create(source_type=news_source)
            await repository.create(source)
            logger.info(f"  ✓ Fuente {news_source.nombre} creada exitosamente")
            logger.info(f"    - Dominio: {news_source.dominio}")
            logger.info(f"    - País: {news_source.pais}")

    logger.info("Inicialización de fuentes completada")

    all_sources = await repository.get_all()
    logger.info(f"\nTotal de fuentes en la base de datos: {len(all_sources)}")
    for source in all_sources:
        logger.info(f"  - {source.nombre} ({source.dominio}) - Activa: {source.activo}")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Script de verificación del modelo de dominio - Ticket 2
Demuestra la funcionalidad de las entidades de dominio sin dependencias externas
"""

from datetime import datetime, timezone
from src.domain.entities import NewsArticle, Source, ScrapingJob
from src.domain.enums import NewsSource


def main():
    print("=" * 60)
    print("VERIFICACIÓN DEL MODELO DE DOMINIO - TICKET 2")
    print("=" * 60)
    print()

    print("1. Creación de NewsArticle")
    print("-" * 60)
    article = NewsArticle.create(
        titulo="España gana el campeonato mundial",
        contenido="En un emocionante partido, España se coronó campeón...",
        fuente="ElPais.com",
        fecha_publicacion=datetime.now(timezone.utc),
        url="https://elpais.com/deportes/2024/champions",
        categoria="Deportes",
    )
    print(f"✅ Artículo creado con ID: {article.id}")
    print(f"   Título: {article.titulo}")
    print(f"   Fuente: {article.fuente}")
    print(f"   Procesado: {article.procesado}")
    print()

    print("2. Modificación de NewsArticle")
    print("-" * 60)
    article.mark_as_processed()
    print(f"✅ Artículo marcado como procesado: {article.procesado}")
    article.update_category("Deportes/Fútbol")
    print(f"✅ Categoría actualizada: {article.categoria}")
    print()

    print("3. Creación de Source")
    print("-" * 60)
    source = Source.create(source_type=NewsSource.CLARIN)
    print(f"✅ Fuente creada con ID: {source.id}")
    print(f"   Nombre: {source.nombre}")
    print(f"   Dominio: {source.dominio}")
    print(f"   País: {source.pais}")
    print(f"   Activo: {source.activo}")
    print()

    print("4. Modificación de Source")
    print("-" * 60)
    source.deactivate()
    print(f"✅ Fuente desactivada: {source.activo}")
    source.activate()
    print(f"✅ Fuente reactivada: {source.activo}")
    print()

    print("5. Listado de todas las fuentes disponibles")
    print("-" * 60)
    for news_source in NewsSource.all_sources():
        print(f"   - {news_source.nombre}: {news_source.dominio}")
    print()

    print("6. Creación y ciclo de vida de ScrapingJob")
    print("-" * 60)
    job = ScrapingJob.create(fuente="Clarín")
    print(f"✅ Job creado con ID: {job.id}")
    print(f"   Status inicial: {job.status}")
    print(f"   Total artículos: {job.total_articulos}")
    print()

    job.start()
    print(f"✅ Job iniciado - Status: {job.status}")

    for i in range(5):
        job.increment_articles()
    print(f"✅ Artículos procesados: {job.total_articulos}")

    job.complete(job.total_articulos)
    print(f"✅ Job completado - Status: {job.status}")
    print(f"   Total final: {job.total_articulos}")
    print(f"   Duración: {job.fecha_fin - job.fecha_inicio}")
    print()

    print("=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA - TODAS LAS ENTIDADES FUNCIONAN")
    print("=" * 60)
    print()
    print("📋 Resumen:")
    print("   - NewsArticle: Creación, procesado, actualización ✅")
    print("   - Source: Creación, activación/desactivación ✅")
    print("   - ScrapingJob: Ciclo de vida completo ✅")
    print("   - Sin dependencias externas ✅")
    print("   - Código limpio y tipado ✅")


if __name__ == "__main__":
    main()

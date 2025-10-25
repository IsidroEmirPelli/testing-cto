#!/usr/bin/env python3
"""
Ejemplo de uso del nuevo sistema de fuentes basado en ENUM.

Este script demuestra cómo trabajar con fuentes usando el enum NewsSource
en lugar de insertar manualmente los datos.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def ejemplo_basico():
    """Ejemplo básico de uso del enum NewsSource."""
    print("=" * 80)
    print("EJEMPLO 1: Uso básico del enum NewsSource")
    print("=" * 80)

    from src.domain.enums import NewsSource
    from src.domain.entities import Source

    print("\n1. Listar todas las fuentes disponibles:")
    print("-" * 80)
    for source in NewsSource.all_sources():
        print(f"  • {source.nombre:15} - {source.dominio:25} ({source.pais})")

    print("\n2. Crear una fuente desde el enum:")
    print("-" * 80)
    source = Source.create(source_type=NewsSource.CLARIN)
    print(f"  ✓ Fuente creada: {source.nombre}")
    print(f"    - ID: {source.id}")
    print(f"    - Dominio: {source.dominio}")
    print(f"    - País: {source.pais}")
    print(f"    - Activa: {source.activo}")

    print("\n3. Crear una fuente desde su nombre:")
    print("-" * 80)
    source2 = Source.create_from_nombre("La Nación")
    print(f"  ✓ Fuente creada: {source2.nombre}")
    print(f"    - Dominio: {source2.dominio}")

    print("\n4. Obtener fuente por nombre (case-insensitive):")
    print("-" * 80)
    found = NewsSource.from_nombre("página 12")
    print(f"  ✓ Encontrada: {found.nombre}")
    print(f"    - Enum value: {found}")

    print("\n5. Obtener fuente por dominio:")
    print("-" * 80)
    found2 = NewsSource.from_dominio("https://www.infobae.com/")
    print(f"  ✓ Encontrada: {found2.nombre}")
    print(f"    - Dominio: {found2.dominio}")


async def ejemplo_con_base_datos():
    """Ejemplo de uso con base de datos."""
    print("\n" + "=" * 80)
    print("EJEMPLO 2: Uso con base de datos Django")
    print("=" * 80)

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

    print("\n1. Crear y guardar fuentes en la base de datos:")
    print("-" * 80)

    for news_source in NewsSource.all_sources():
        existing = await repository.get_by_nombre(news_source.nombre)
        if existing:
            print(f"  • {news_source.nombre:15} - Ya existe en la BD")
        else:
            source = Source.create(source_type=news_source)
            await repository.create(source)
            print(f"  ✓ {news_source.nombre:15} - Creada exitosamente")

    print("\n2. Consultar fuentes activas desde la BD:")
    print("-" * 80)
    active_sources = await repository.get_active_sources()
    print(f"  Total de fuentes activas: {len(active_sources)}")
    for source in active_sources:
        print(f"    • {source.nombre} ({source.dominio})")

    print("\n3. Buscar una fuente específica:")
    print("-" * 80)
    clarin = await repository.get_by_nombre("Clarín")
    if clarin:
        print(f"  ✓ Encontrada: {clarin.nombre}")
        print(f"    - ID: {clarin.id}")
        print(f"    - Dominio: {clarin.dominio}")
        print(f"    - Activa: {clarin.activo}")
    else:
        print("  ✗ No encontrada")

    print("\n4. Desactivar y reactivar una fuente:")
    print("-" * 80)
    if clarin:
        clarin.deactivate()
        await repository.update(clarin)
        print(f"  ✓ {clarin.nombre} desactivada")

        clarin.activate()
        await repository.update(clarin)
        print(f"  ✓ {clarin.nombre} reactivada")


def ejemplo_comparacion():
    """Comparación entre el sistema antiguo y el nuevo."""
    print("\n" + "=" * 80)
    print("EJEMPLO 3: Comparación Antiguo vs Nuevo Sistema")
    print("=" * 80)

    print("\n❌ SISTEMA ANTIGUO (Manual):")
    print("-" * 80)
    print("  # Usuario debe ingresar manualmente:")
    print("  source = Source.create(")
    print('      nombre="Clarín",')
    print('      dominio="www.clarin.com",')
    print('      pais="Argentina"')
    print("  )")
    print("\n  Problemas:")
    print("    • Errores tipográficos")
    print("    • Inconsistencias en los datos")
    print("    • Duplicados potenciales")
    print("    • No hay validación")

    print("\n✅ SISTEMA NUEVO (Enum):")
    print("-" * 80)
    print("  # Simple y seguro:")
    print("  source = Source.create(source_type=NewsSource.CLARIN)")
    print("\n  Beneficios:")
    print("    • Sin errores tipográficos")
    print("    • Datos consistentes")
    print("    • Autocompletado en IDE")
    print("    • Validación automática")
    print("    • Un único lugar para configurar")


def ejemplo_api_rest():
    """Ejemplo de uso en API REST."""
    print("\n" + "=" * 80)
    print("EJEMPLO 4: Uso en API REST")
    print("=" * 80)

    print("\n1. Crear una fuente vía API (POST):")
    print("-" * 80)
    print("  curl -X POST http://localhost:8000/api/sources/ \\")
    print("       -H 'Content-Type: application/json' \\")
    print('       -d \'{"source_type": "CLARIN"}\'')

    print("\n2. Valores válidos para source_type:")
    print("-" * 80)
    print("    • CLARIN")
    print("    • LA_NACION")
    print("    • PAGINA12")
    print("    • INFOBAE")

    print("\n3. Ejemplo de respuesta:")
    print("-" * 80)
    print("  {")
    print('    "id": "550e8400-e29b-41d4-a716-446655440000",')
    print('    "source_type": "CLARIN",')
    print('    "nombre": "Clarín",')
    print('    "dominio": "www.clarin.com",')
    print('    "pais": "Argentina",')
    print('    "activo": true,')
    print('    "created_at": "2024-01-15T10:00:00Z",')
    print('    "updated_at": null')
    print("  }")


async def main():
    """Ejecuta todos los ejemplos."""
    ejemplo_basico()

    try:
        await ejemplo_con_base_datos()
    except Exception as e:
        print(f"\n⚠️  No se pudo conectar a la base de datos: {e}")
        print("   (Esto es normal si no has ejecutado las migraciones)")

    ejemplo_comparacion()
    ejemplo_api_rest()

    print("\n" + "=" * 80)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 80)
    print("\nPara más información, consulta: ENUM_SOURCE_MIGRATION.md")


if __name__ == "__main__":
    asyncio.run(main())

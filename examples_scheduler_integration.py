#!/usr/bin/env python3
"""
Ejemplos de integración del coordinador de scraping con diferentes sistemas de programación.

Este archivo contiene ejemplos prácticos de cómo integrar ScrapeAllSourcesUseCase
con diferentes sistemas de programación de tareas (schedulers).
"""

import asyncio
import logging
from datetime import datetime
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from src.application.use_cases import ScrapeAllSourcesUseCase
from src.infrastructure.persistence.django_repositories import (
    DjangoSourceRepository,
    DjangoScrapingJobRepository,
    DjangoNewsArticleRepository,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURACIÓN COMÚN
# =============================================================================


def setup_django():
    """Inicializar Django para usar ORM."""
    import django

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "src.infrastructure.config.django_settings"
    )
    django.setup()


async def execute_scraping_coordinator():
    """
    Función común que ejecuta el coordinador de scraping.
    Puede ser llamada desde cualquier scheduler.
    """
    try:
        setup_django()

        # Crear repositorios
        source_repo = DjangoSourceRepository()
        job_repo = DjangoScrapingJobRepository()
        article_repo = DjangoNewsArticleRepository()

        # Crear caso de uso
        scrape_all = ScrapeAllSourcesUseCase(
            source_repository=source_repo,
            scraping_job_repository=job_repo,
            article_repository=article_repo,
        )

        # Ejecutar
        logger.info("Iniciando coordinador de scraping programado")
        result = await scrape_all.execute()

        # Log de resultados
        logger.info(
            f"Coordinador finalizado - Artículos scrapeados: {result['total_articles_scraped']}"
        )
        logger.info(f"Artículos nuevos guardados: {result['total_articles_persisted']}")

        return result

    except Exception as e:
        logger.error(f"Error en coordinador programado: {e}", exc_info=True)
        raise


# =============================================================================
# EJEMPLO 1: CRON
# =============================================================================


def example_cron_setup():
    """
    Ejemplo de configuración con cron.

    Para usar con cron, ejecutar este script directamente y configurar crontab:

    # Editar crontab
    crontab -e

    # Agregar línea para ejecutar diariamente a las 6 AM
    0 6 * * * cd /path/to/project && /path/to/venv/bin/python demo_scrape_all_sources.py >> /var/log/scraping.log 2>&1

    # O cada 4 horas
    0 */4 * * * cd /path/to/project && /path/to/venv/bin/python demo_scrape_all_sources.py >> /var/log/scraping.log 2>&1

    # Verificar que se agregó
    crontab -l
    """
    print(
        "Para configurar con cron, seguir las instrucciones en los comentarios de esta función"
    )
    print("Básicamente: ejecutar demo_scrape_all_sources.py desde crontab")


# =============================================================================
# EJEMPLO 2: APScheduler
# =============================================================================


def example_apscheduler():
    """
    Ejemplo de integración con APScheduler.

    APScheduler es un scheduler Python avanzado que soporta:
    - Cron-style scheduling
    - Interval-based scheduling
    - Date-based scheduling
    """
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        print("APScheduler no está instalado. Instalar con: pip install apscheduler")
        return

    async def scheduled_job():
        """Job que será ejecutado por el scheduler."""
        try:
            result = await execute_scraping_coordinator()
            logger.info(
                f"Job programado completado - Jobs exitosos: {result['total_jobs_completed']}"
            )
        except Exception as e:
            logger.error(f"Error en job programado: {e}")

    # Crear scheduler
    scheduler = AsyncIOScheduler()

    # Opción 1: Ejecutar cada día a las 6 AM
    scheduler.add_job(
        scheduled_job,
        CronTrigger(hour=6, minute=0),
        id="daily_scraping_6am",
        name="Scraping Diario 6 AM",
        replace_existing=True,
    )

    # Opción 2: Ejecutar cada 4 horas
    scheduler.add_job(
        scheduled_job,
        "interval",
        hours=4,
        id="scraping_every_4h",
        name="Scraping cada 4 horas",
        replace_existing=True,
    )

    # Opción 3: Ejecutar de lunes a viernes a las 9 AM
    scheduler.add_job(
        scheduled_job,
        CronTrigger(day_of_week="mon-fri", hour=9, minute=0),
        id="weekday_scraping",
        name="Scraping días laborales",
        replace_existing=True,
    )

    # Iniciar scheduler
    scheduler.start()
    logger.info("APScheduler iniciado. Jobs programados:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name} (ID: {job.id})")

    # Mantener el programa corriendo
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Deteniendo scheduler...")
        scheduler.shutdown()


# =============================================================================
# EJEMPLO 3: Celery
# =============================================================================


def example_celery_setup():
    """
    Ejemplo de configuración con Celery.

    Celery es un sistema de cola de tareas distribuido para Python.
    Ideal para aplicaciones grandes con múltiples workers.
    """
    print(
        """
    # 1. Instalar Celery y un message broker (Redis o RabbitMQ)
    pip install celery redis
    
    # 2. Crear archivo celery_tasks.py:
    
    from celery import Celery
    import asyncio
    from examples_scheduler_integration import execute_scraping_coordinator
    
    # Configurar Celery
    app = Celery('scraping_tasks', broker='redis://localhost:6379/0')
    
    @app.task
    def scrape_all_sources_task():
        '''Tarea Celery para ejecutar el coordinador de scraping'''
        return asyncio.run(execute_scraping_coordinator())
    
    # Configurar beat schedule
    app.conf.beat_schedule = {
        'scrape-daily-6am': {
            'task': 'celery_tasks.scrape_all_sources_task',
            'schedule': crontab(hour=6, minute=0),
        },
        'scrape-every-4-hours': {
            'task': 'celery_tasks.scrape_all_sources_task',
            'schedule': crontab(minute=0, hour='*/4'),
        },
    }
    
    # 3. Ejecutar el worker
    # celery -A celery_tasks worker --loglevel=info
    
    # 4. Ejecutar el beat scheduler
    # celery -A celery_tasks beat --loglevel=info
    
    # 5. O ejecutar ambos juntos
    # celery -A celery_tasks worker --beat --loglevel=info
    """
    )


# =============================================================================
# EJEMPLO 4: Django-Celery-Beat (integración con Django)
# =============================================================================


def example_django_celery_beat():
    """
    Ejemplo de configuración con Django-Celery-Beat.

    Permite gestionar tareas programadas desde el admin de Django.
    """
    print(
        """
    # 1. Instalar django-celery-beat
    pip install django-celery-beat
    
    # 2. Agregar a INSTALLED_APPS en settings.py
    INSTALLED_APPS = [
        ...
        'django_celery_beat',
    ]
    
    # 3. Ejecutar migraciones
    python manage.py migrate
    
    # 4. Crear tarea en celery_tasks.py:
    
    from celery import shared_task
    import asyncio
    from examples_scheduler_integration import execute_scraping_coordinator
    
    @shared_task
    def scrape_all_sources_task():
        return asyncio.run(execute_scraping_coordinator())
    
    # 5. Crear la tarea programada desde el admin de Django:
    # - Ir a http://localhost:8000/admin/django_celery_beat/periodictask/
    # - Crear nueva tarea periódica
    # - Seleccionar la tarea 'scrape_all_sources_task'
    # - Configurar el schedule (cron, interval, etc.)
    
    # 6. Ejecutar worker y beat
    # celery -A project worker --beat --loglevel=info
    """
    )


# =============================================================================
# EJEMPLO 5: Schedule (Simple Python Scheduler)
# =============================================================================


def example_schedule():
    """
    Ejemplo con la librería 'schedule' - Simple y ligero.

    Ideal para aplicaciones pequeñas o prototipos.
    """
    try:
        import schedule
        import time
    except ImportError:
        print("Schedule no está instalado. Instalar con: pip install schedule")
        return

    def job():
        """Función wrapper para ejecutar el coordinador."""
        try:
            result = asyncio.run(execute_scraping_coordinator())
            logger.info(
                f"Job completado - Artículos: {result['total_articles_scraped']}"
            )
        except Exception as e:
            logger.error(f"Error en job: {e}")

    # Configurar schedules
    schedule.every().day.at("06:00").do(job)  # Diario a las 6 AM
    schedule.every(4).hours.do(job)  # Cada 4 horas
    schedule.every().monday.at("09:00").do(job)  # Lunes a las 9 AM

    logger.info("Schedule iniciado. Jobs programados:")
    for job_obj in schedule.get_jobs():
        logger.info(f"  - {job_obj}")

    # Ejecutar el loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar cada minuto


# =============================================================================
# EJEMPLO 6: Ejecución Manual/One-Time
# =============================================================================


async def example_manual_execution():
    """
    Ejemplo de ejecución manual - útil para testing o ejecuciones únicas.
    """
    logger.info("Ejecutando coordinador de scraping manualmente...")
    result = await execute_scraping_coordinator()

    print("\n" + "=" * 80)
    print("RESULTADOS DE EJECUCIÓN MANUAL")
    print("=" * 80)
    print(f"Fuentes procesadas: {result['total_sources']}")
    print(f"Jobs completados: {result['total_jobs_completed']}")
    print(f"Jobs fallidos: {result['total_jobs_failed']}")
    print(f"Artículos scrapeados: {result['total_articles_scraped']}")
    print(f"Artículos guardados: {result['total_articles_persisted']}")
    print("=" * 80)


# =============================================================================
# EJEMPLO 7: AWS Lambda (Serverless)
# =============================================================================


def example_aws_lambda():
    """
    Ejemplo de configuración para AWS Lambda.

    Permite ejecutar el scraping en un ambiente serverless.
    """
    print(
        """
    # 1. Crear archivo lambda_handler.py:
    
    import asyncio
    from examples_scheduler_integration import execute_scraping_coordinator
    
    def lambda_handler(event, context):
        '''Handler para AWS Lambda'''
        try:
            result = asyncio.run(execute_scraping_coordinator())
            
            return {
                'statusCode': 200,
                'body': {
                    'message': 'Scraping completado',
                    'stats': result
                }
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': {
                    'message': 'Error en scraping',
                    'error': str(e)
                }
            }
    
    # 2. Empaquetar la aplicación con dependencias
    # pip install -r requirements.txt -t ./package
    # cd package && zip -r ../lambda_function.zip .
    # cd .. && zip -g lambda_function.zip lambda_handler.py src/
    
    # 3. Subir a AWS Lambda
    # aws lambda create-function --function-name scraping-coordinator \\
    #     --runtime python3.11 --handler lambda_handler.lambda_handler \\
    #     --zip-file fileb://lambda_function.zip --role <IAM_ROLE_ARN>
    
    # 4. Configurar CloudWatch Events para ejecutar programadamente
    # - Crear regla de CloudWatch Events con schedule expression: cron(0 6 * * ? *)
    # - Asociar la función Lambda como target
    """
    )


# =============================================================================
# MENÚ PRINCIPAL
# =============================================================================


def main():
    """Menú principal para seleccionar el ejemplo a ejecutar."""
    print("\n" + "=" * 80)
    print("EJEMPLOS DE INTEGRACIÓN DEL COORDINADOR DE SCRAPING")
    print("=" * 80)
    print("\nSeleccione el ejemplo que desea ver/ejecutar:\n")
    print("1. Cron - Configuración básica")
    print("2. APScheduler - Scheduler Python avanzado")
    print("3. Celery - Sistema de colas distribuido")
    print("4. Django-Celery-Beat - Integración con Django")
    print("5. Schedule - Scheduler Python simple")
    print("6. Ejecución Manual - Testing y debugging")
    print("7. AWS Lambda - Serverless")
    print("0. Salir")

    choice = input("\nOpción: ").strip()

    examples = {
        "1": example_cron_setup,
        "2": example_apscheduler,
        "3": example_celery_setup,
        "4": example_django_celery_beat,
        "5": example_schedule,
        "6": lambda: asyncio.run(example_manual_execution()),
        "7": example_aws_lambda,
    }

    if choice == "0":
        print("Saliendo...")
        return

    example = examples.get(choice)
    if example:
        print(f"\n{'='*80}")
        example()
        print(f"{'='*80}\n")
    else:
        print("Opción inválida")


if __name__ == "__main__":
    main()

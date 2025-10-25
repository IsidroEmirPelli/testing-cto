import pytest
from datetime import datetime

from src.domain.entities.scraping_job import ScrapingJob


def test_create_scraping_job():
    fuente = "test.com"

    job = ScrapingJob.create(fuente=fuente)

    assert job.fuente == fuente
    assert job.status == "pending"
    assert job.total_articulos == 0
    assert job.fecha_inicio is not None
    assert job.fecha_fin is None
    assert job.id is not None
    assert job.created_at is not None
    assert job.updated_at is None


def test_start_job():
    job = ScrapingJob.create(fuente="test.com")

    job.start()

    assert job.status == "running"
    assert job.updated_at is not None


def test_complete_job():
    job = ScrapingJob.create(fuente="test.com")
    total_articulos = 10

    job.complete(total_articulos)

    assert job.status == "completed"
    assert job.total_articulos == total_articulos
    assert job.fecha_fin is not None
    assert job.updated_at is not None


def test_fail_job():
    job = ScrapingJob.create(fuente="test.com")

    job.fail()

    assert job.status == "failed"
    assert job.fecha_fin is not None
    assert job.updated_at is not None


def test_increment_articles():
    job = ScrapingJob.create(fuente="test.com")

    job.increment_articles()
    assert job.total_articulos == 1

    job.increment_articles()
    assert job.total_articulos == 2

    job.increment_articles()
    assert job.total_articulos == 3
    assert job.updated_at is not None

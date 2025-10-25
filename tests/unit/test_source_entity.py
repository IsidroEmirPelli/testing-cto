import pytest
from datetime import datetime

from src.domain.entities.source import Source
from src.domain.enums import NewsSource


def test_create_source():
    source_type = NewsSource.CLARIN

    source = Source.create(source_type=source_type)

    assert source.nombre == "Clarín"
    assert source.dominio == "www.clarin.com"
    assert source.pais == "Argentina"
    assert source.activo is True
    assert source.id is not None
    assert source.created_at is not None
    assert source.updated_at is None


def test_create_source_from_nombre():
    source = Source.create_from_nombre("La Nación")

    assert source.nombre == "La Nación"
    assert source.dominio == "www.lanacion.com.ar"
    assert source.pais == "Argentina"
    assert source.activo is True


def test_deactivate_source():
    source = Source.create(source_type=NewsSource.PAGINA12)

    source.deactivate()

    assert source.activo is False
    assert source.updated_at is not None


def test_activate_source():
    source = Source.create(source_type=NewsSource.INFOBAE)
    source.deactivate()

    source.activate()

    assert source.activo is True
    assert source.updated_at is not None


def test_news_source_from_nombre():
    source = NewsSource.from_nombre("Clarín")
    assert source == NewsSource.CLARIN

    source = NewsSource.from_nombre("la nación")
    assert source == NewsSource.LA_NACION


def test_news_source_from_dominio():
    source = NewsSource.from_dominio("www.clarin.com")
    assert source == NewsSource.CLARIN

    source = NewsSource.from_dominio("https://www.pagina12.com.ar/")
    assert source == NewsSource.PAGINA12

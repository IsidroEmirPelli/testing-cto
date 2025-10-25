import pytest
from datetime import datetime

from src.domain.entities.source import Source


def test_create_source():
    nombre = "Test News"
    dominio = "test.com"
    pais = "ES"

    source = Source.create(nombre=nombre, dominio=dominio, pais=pais)

    assert source.nombre == nombre
    assert source.dominio == dominio
    assert source.pais == pais
    assert source.activo is True
    assert source.id is not None
    assert source.created_at is not None
    assert source.updated_at is None


def test_deactivate_source():
    source = Source.create(nombre="Test News", dominio="test.com", pais="ES")

    source.deactivate()

    assert source.activo is False
    assert source.updated_at is not None


def test_activate_source():
    source = Source.create(nombre="Test News", dominio="test.com", pais="ES")
    source.deactivate()

    source.activate()

    assert source.activo is True
    assert source.updated_at is not None


def test_update_info():
    source = Source.create(
        nombre="Original Name", dominio="original.com", pais="ES"
    )

    new_nombre = "Updated Name"
    new_dominio = "updated.com"
    new_pais = "US"
    source.update_info(new_nombre, new_dominio, new_pais)

    assert source.nombre == new_nombre
    assert source.dominio == new_dominio
    assert source.pais == new_pais
    assert source.updated_at is not None

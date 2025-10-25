import pytest
from datetime import datetime, timezone

from src.domain.entities.news_article import NewsArticle


def test_create_news_article():
    titulo = "Test Article"
    contenido = "Test content"
    fuente = "Test Source"
    fecha_publicacion = datetime.now(timezone.utc)
    url = "https://example.com/article"
    categoria = "Technology"

    article = NewsArticle.create(
        titulo=titulo,
        contenido=contenido,
        fuente=fuente,
        fecha_publicacion=fecha_publicacion,
        url=url,
        categoria=categoria,
    )

    assert article.titulo == titulo
    assert article.contenido == contenido
    assert article.fuente == fuente
    assert article.fecha_publicacion == fecha_publicacion
    assert article.url == url
    assert article.categoria == categoria
    assert article.procesado is False
    assert article.id is not None
    assert article.created_at is not None
    assert article.updated_at is None


def test_create_news_article_without_categoria():
    article = NewsArticle.create(
        titulo="Test",
        contenido="Content",
        fuente="Source",
        fecha_publicacion=datetime.now(timezone.utc),
        url="https://test.com",
    )

    assert article.categoria is None
    assert article.procesado is False


def test_mark_as_processed():
    article = NewsArticle.create(
        titulo="Test",
        contenido="Content",
        fuente="Source",
        fecha_publicacion=datetime.now(timezone.utc),
        url="https://test.com",
    )
    original_created_at = article.created_at

    article.mark_as_processed()

    assert article.procesado is True
    assert article.updated_at is not None
    assert article.updated_at > original_created_at


def test_update_content():
    article = NewsArticle.create(
        titulo="Original Title",
        contenido="Original Content",
        fuente="Source",
        fecha_publicacion=datetime.now(timezone.utc),
        url="https://test.com",
    )

    new_titulo = "Updated Title"
    new_contenido = "Updated Content"
    article.update_content(new_titulo, new_contenido)

    assert article.titulo == new_titulo
    assert article.contenido == new_contenido
    assert article.updated_at is not None


def test_update_category():
    article = NewsArticle.create(
        titulo="Test",
        contenido="Content",
        fuente="Source",
        fecha_publicacion=datetime.now(timezone.utc),
        url="https://test.com",
    )

    new_categoria = "Sports"
    article.update_category(new_categoria)

    assert article.categoria == new_categoria
    assert article.updated_at is not None

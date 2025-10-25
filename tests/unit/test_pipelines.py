import pytest
from datetime import datetime, timezone

from src.infrastructure.external_services.scrapy_adapter.pipelines import (
    TextCleaningPipeline,
    ValidationPipeline,
)
from src.infrastructure.external_services.scrapy_adapter.items import NewsArticleItem


class TestTextCleaningPipeline:
    def test_clean_html_content(self):
        pipeline = TextCleaningPipeline()

        html_content = """
        <div>
            <script>alert('test');</script>
            <p>Este es un párrafo.</p>
            <p>Este es otro párrafo.</p>
            <nav>Menu</nav>
        </div>
        """

        cleaned = pipeline._clean_html_content(html_content)

        assert "alert" not in cleaned
        assert "Menu" not in cleaned
        assert "párrafo" in cleaned

    def test_clean_text_removes_extra_whitespace(self):
        pipeline = TextCleaningPipeline()

        text = "Este  es    un   texto   con    espacios    extras"
        cleaned = pipeline._clean_text(text)

        assert cleaned == "Este es un texto con espacios extras"

    def test_clean_text_removes_special_chars(self):
        pipeline = TextCleaningPipeline()

        text = "Texto\xa0con\u200bespacios\xa0especiales"
        cleaned = pipeline._clean_text(text)

        assert "\xa0" not in cleaned
        assert "\u200b" not in cleaned

    def test_process_item_cleans_titulo_and_contenido(self):
        pipeline = TextCleaningPipeline()

        item = NewsArticleItem()
        item["titulo"] = "  Título   con   espacios  "
        item["contenido"] = "<p>Contenido con HTML</p>"
        item["fuente"] = "Test"
        item["url"] = "https://test.com"
        item["fecha_publicacion"] = datetime.now(timezone.utc)

        processed = pipeline.process_item(item, None)

        assert processed["titulo"] == "Título con espacios"
        assert "HTML" in processed["contenido"]
        assert "<p>" not in processed["contenido"]


class TestValidationPipeline:
    def test_valid_item_passes(self):
        pipeline = ValidationPipeline()

        item = NewsArticleItem()
        item["titulo"] = "Test Title"
        item["contenido"] = "Este es un contenido suficientemente largo. " * 10
        item["fuente"] = "Test Source"
        item["url"] = "https://test.com/article"
        item["fecha_publicacion"] = datetime.now(timezone.utc)

        result = pipeline.process_item(item, None)

        assert result is item

    def test_missing_required_field_raises_exception(self):
        pipeline = ValidationPipeline()

        item = NewsArticleItem()
        item["titulo"] = "Test Title"
        item["fuente"] = "Test Source"

        with pytest.raises(Exception, match="Campo requerido faltante"):
            pipeline.process_item(item, None)

    def test_short_content_raises_exception(self):
        pipeline = ValidationPipeline()

        item = NewsArticleItem()
        item["titulo"] = "Test Title"
        item["contenido"] = "Muy corto"
        item["fuente"] = "Test Source"
        item["url"] = "https://test.com/article"

        with pytest.raises(Exception, match="Contenido demasiado corto"):
            pipeline.process_item(item, None)

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from src.infrastructure.external_services.scrapy_adapter import ScrapyAdapter
from src.infrastructure.external_services.mock_queue import MockQueue
from src.domain.entities.news_article import NewsArticle


class TestScrapyAdapter:
    def test_adapter_initialization(self):
        adapter = ScrapyAdapter()
        assert adapter is not None
        assert adapter.queue is not None
        assert isinstance(adapter.queue, MockQueue)
        assert adapter.scraped_articles == []

    def test_adapter_with_custom_queue(self):
        custom_queue = MockQueue()
        adapter = ScrapyAdapter(queue=custom_queue)
        assert adapter.queue is custom_queue

    def test_spider_map_has_all_sources(self):
        expected_sources = ["clarin", "lanacion", "infobae", "pagina12"]
        for source in expected_sources:
            assert source in ScrapyAdapter.SPIDER_MAP

    def test_get_queue(self):
        queue = MockQueue()
        adapter = ScrapyAdapter(queue=queue)
        assert adapter.get_queue() is queue


class TestMockQueue:
    def test_queue_initialization(self):
        queue = MockQueue()
        assert queue.is_empty()
        assert queue.size() == 0

    def test_enqueue_article(self):
        queue = MockQueue()
        article = NewsArticle.create(
            titulo="Test Article",
            contenido="Test content " * 50,
            fuente="Test Source",
            fecha_publicacion=datetime.now(timezone.utc),
            url="https://test.com/article",
        )
        queue.enqueue(article)

        assert not queue.is_empty()
        assert queue.size() == 1

    def test_dequeue_article(self):
        queue = MockQueue()
        article = NewsArticle.create(
            titulo="Test Article",
            contenido="Test content " * 50,
            fuente="Test Source",
            fecha_publicacion=datetime.now(timezone.utc),
            url="https://test.com/article",
        )
        queue.enqueue(article)

        dequeued = queue.dequeue()

        assert dequeued is not None
        assert dequeued.titulo == "Test Article"
        assert queue.is_empty()

    def test_dequeue_empty_queue(self):
        queue = MockQueue()
        result = queue.dequeue()
        assert result is None

    def test_enqueue_batch(self):
        queue = MockQueue()
        articles = [
            NewsArticle.create(
                titulo=f"Article {i}",
                contenido="Test content " * 50,
                fuente="Test Source",
                fecha_publicacion=datetime.now(timezone.utc),
                url=f"https://test.com/article{i}",
            )
            for i in range(5)
        ]

        queue.enqueue_batch(articles)

        assert queue.size() == 5

    def test_clear_queue(self):
        queue = MockQueue()
        articles = [
            NewsArticle.create(
                titulo=f"Article {i}",
                contenido="Test content " * 50,
                fuente="Test Source",
                fecha_publicacion=datetime.now(timezone.utc),
                url=f"https://test.com/article{i}",
            )
            for i in range(3)
        ]
        queue.enqueue_batch(articles)

        assert queue.size() == 3
        queue.clear()
        assert queue.is_empty()

    def test_get_all(self):
        queue = MockQueue()
        articles = [
            NewsArticle.create(
                titulo=f"Article {i}",
                contenido="Test content " * 50,
                fuente="Test Source",
                fecha_publicacion=datetime.now(timezone.utc),
                url=f"https://test.com/article{i}",
            )
            for i in range(3)
        ]
        queue.enqueue_batch(articles)

        all_articles = queue.get_all()

        assert len(all_articles) == 3
        assert queue.size() == 3

import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from src.application.use_cases.scrape_news import ScrapeNewsUseCase
from src.domain.entities.news_article import NewsArticle


class TestScrapeNewsUseCase:
    def test_execute_returns_dtos(self):
        mock_scraper = Mock()

        mock_articles = [
            NewsArticle.create(
                titulo="Test Article 1",
                contenido="Content for article 1 " * 20,
                fuente="Test Source",
                fecha_publicacion=datetime.now(timezone.utc),
                url="https://test.com/article1",
            ),
            NewsArticle.create(
                titulo="Test Article 2",
                contenido="Content for article 2 " * 20,
                fuente="Test Source",
                fecha_publicacion=datetime.now(timezone.utc),
                url="https://test.com/article2",
            ),
        ]

        mock_scraper.scrape_sources.return_value = mock_articles

        use_case = ScrapeNewsUseCase(scraper=mock_scraper)

        result = use_case.execute(["test_source"])

        assert len(result) == 2
        assert result[0].titulo == "Test Article 1"
        assert result[1].titulo == "Test Article 2"

        mock_scraper.scrape_sources.assert_called_once_with(["test_source"])

    def test_execute_with_empty_result(self):
        mock_scraper = Mock()
        mock_scraper.scrape_sources.return_value = []

        use_case = ScrapeNewsUseCase(scraper=mock_scraper)

        result = use_case.execute(["test_source"])

        assert len(result) == 0

    def test_execute_propagates_exception(self):
        mock_scraper = Mock()
        mock_scraper.scrape_sources.side_effect = Exception("Scraping failed")

        use_case = ScrapeNewsUseCase(scraper=mock_scraper)

        with pytest.raises(Exception, match="Scraping failed"):
            use_case.execute(["test_source"])

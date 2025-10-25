"""
Tests unitarios para el scraper de Clarín.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from src.infrastructure.adapters.scrapers.clarin_scraper import ClarinScraper
from src.domain.dto.article_dto import ArticleDTO


class TestClarinScraper:
    """Tests para el ClarinScraper"""
    
    def test_scraper_initialization(self):
        """Test de inicialización del scraper"""
        scraper = ClarinScraper(max_articles=10, timeout=20)
        
        assert scraper.base_url == "https://www.clarin.com"
        assert scraper.max_articles == 10
        assert scraper.timeout == 20
        assert scraper.session is not None
    
    def test_scraper_default_initialization(self):
        """Test de inicialización con valores por defecto"""
        scraper = ClarinScraper()
        
        assert scraper.max_articles == 15
        assert scraper.timeout == 30
    
    @patch('src.infrastructure.adapters.scrapers.clarin_scraper.requests.Session')
    def test_scrape_returns_list(self, mock_session_class):
        """Test que scrape() retorna una lista"""
        # Mock de la sesión que retorna respuestas vacías
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock de respuesta vacía
        mock_response = Mock()
        mock_response.content = b"<html><body></body></html>"
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        
        scraper = ClarinScraper(max_articles=1)
        articles = scraper.scrape()
        
        # Debe retornar una lista (puede estar vacía si no hay contenido)
        assert isinstance(articles, list)
    
    def test_extract_title_from_different_selectors(self):
        """Test extracción de título con diferentes selectores"""
        from bs4 import BeautifulSoup
        
        scraper = ClarinScraper()
        
        # Test con h1 class="title"
        html1 = '<html><body><h1 class="title">Test Title 1</h1></body></html>'
        soup1 = BeautifulSoup(html1, 'lxml')
        title1 = scraper._extract_title(soup1)
        assert title1 == "Test Title 1"
        
        # Test con h1 sin clase
        html2 = '<html><body><h1>Test Title 2</h1></body></html>'
        soup2 = BeautifulSoup(html2, 'lxml')
        title2 = scraper._extract_title(soup2)
        assert title2 == "Test Title 2"
        
        # Test con meta og:title
        html3 = '<html><head><meta property="og:title" content="Test Title 3"></head></html>'
        soup3 = BeautifulSoup(html3, 'lxml')
        title3 = scraper._extract_title(soup3)
        assert title3 == "Test Title 3"
    
    def test_extract_content_from_paragraphs(self):
        """Test extracción de contenido de párrafos"""
        from bs4 import BeautifulSoup
        
        scraper = ClarinScraper()
        
        html = '''
        <html>
            <body>
                <div class="body-nota">
                    <p>First paragraph.</p>
                    <p>Second paragraph.</p>
                    <p>Third paragraph.</p>
                </div>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'lxml')
        content = scraper._extract_content(soup)
        
        assert "First paragraph." in content
        assert "Second paragraph." in content
        assert "Third paragraph." in content
    
    def test_extract_publication_date_from_meta(self):
        """Test extracción de fecha de publicación"""
        from bs4 import BeautifulSoup
        
        scraper = ClarinScraper()
        
        # Test con meta article:published_time
        html = '<html><head><meta property="article:published_time" content="2024-10-25T10:30:00Z"></head></html>'
        soup = BeautifulSoup(html, 'lxml')
        date = scraper._extract_publication_date(soup)
        
        assert date is not None
        assert isinstance(date, datetime)
    
    def test_extract_publication_date_defaults_to_now(self):
        """Test que fecha de publicación por defecto es ahora"""
        from bs4 import BeautifulSoup
        
        scraper = ClarinScraper()
        
        html = '<html><body></body></html>'
        soup = BeautifulSoup(html, 'lxml')
        date = scraper._extract_publication_date(soup)
        
        assert date is not None
        assert isinstance(date, datetime)
        # Verificar que es una fecha reciente (dentro de los últimos segundos)
        now = datetime.now(timezone.utc)
        diff = (now - date).total_seconds()
        assert diff < 5  # Menos de 5 segundos de diferencia
    
    def test_article_dto_has_required_fields(self):
        """Test que ArticleDTO tiene los campos requeridos"""
        article = ArticleDTO(
            titulo="Test Title",
            url="https://www.clarin.com/test",
            contenido="Test content",
            fecha_publicacion=datetime.now(timezone.utc),
            fuente="Clarín"
        )
        
        assert article.titulo == "Test Title"
        assert article.url == "https://www.clarin.com/test"
        assert article.contenido == "Test content"
        assert article.fecha_publicacion is not None
        assert article.fuente == "Clarín"
    
    def test_scraper_handles_network_errors_gracefully(self):
        """Test que el scraper maneja errores de red apropiadamente"""
        with patch('src.infrastructure.adapters.scrapers.clarin_scraper.requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_session.get.side_effect = Exception("Network error")
            
            scraper = ClarinScraper(max_articles=1)
            articles = scraper.scrape()
            
            # Debería retornar lista vacía o manejar el error
            assert isinstance(articles, list)
    
    def test_scraper_filters_unwanted_urls(self):
        """Test que el scraper filtra URLs no deseadas"""
        from bs4 import BeautifulSoup
        
        scraper = ClarinScraper()
        
        html = '''
        <html>
            <body>
                <article>
                    <a href="/tema/politics">Tema</a>
                    <a href="/tags/news">Tags</a>
                    <a href="/autor/john">Autor</a>
                    <a href="/politica/valid-article">Valid</a>
                </article>
            </body>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.content = html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        
        with patch.object(scraper.session, 'get', return_value=mock_response):
            urls = scraper._extract_article_urls_from_section("https://www.clarin.com/politica/")
            
            # No debería incluir URLs con /tema/, /tags/, /autor/
            assert not any('/tema/' in url for url in urls)
            assert not any('/tags/' in url for url in urls)
            assert not any('/autor/' in url for url in urls)

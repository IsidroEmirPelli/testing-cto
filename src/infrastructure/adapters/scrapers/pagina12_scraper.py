import logging
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.domain.dto.article_dto import ArticleDTO

logger = logging.getLogger(__name__)


class Pagina12Scraper:
    """
    Scraper específico para extraer artículos del sitio web de Página 12.
    
    Implementa la interfaz ScraperPort de forma estructural (Protocol),
    extrayendo artículos de las secciones principales del periódico.
    
    Attributes:
        base_url: URL base del sitio de Página 12
        max_articles: Número máximo de artículos a extraer por sesión
        timeout: Tiempo máximo de espera para las peticiones HTTP (en segundos)
    """
    
    def __init__(self, max_articles: int = 15, timeout: int = 30):
        self.base_url = "https://www.pagina12.com.ar"
        self.max_articles = max_articles
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        logger.info(f"Pagina12Scraper inicializado - max_articles: {max_articles}")
    
    def scrape(self) -> list[ArticleDTO]:
        """
        Extrae artículos de las secciones configuradas de Página 12.
        
        Returns:
            list[ArticleDTO]: Lista de artículos extraídos en formato estandarizado
            
        Raises:
            Exception: Si ocurre un error crítico durante el proceso de scraping
        """
        logger.info("Iniciando scraping de Página 12")
        articles = []
        
        sections = [
            '/secciones/el-pais',
            '/secciones/economia',
            '/secciones/sociedad',
        ]
        
        article_urls = set()
        
        # Fase 1: Recolectar URLs de artículos de las secciones
        for section in sections:
            if len(article_urls) >= self.max_articles:
                break
            
            try:
                section_url = urljoin(self.base_url, section)
                logger.info(f"Extrayendo URLs de sección: {section_url}")
                urls = self._extract_article_urls_from_section(section_url)
                article_urls.update(urls)
                logger.info(f"URLs extraídas de {section}: {len(urls)}")
            except Exception as e:
                logger.error(f"Error extrayendo URLs de sección {section}: {e}", exc_info=True)
        
        # Fase 2: Extraer contenido de cada artículo
        article_urls_list = list(article_urls)[:self.max_articles]
        logger.info(f"Extrayendo contenido de {len(article_urls_list)} artículos")
        
        for url in article_urls_list:
            try:
                article = self._extract_article_content(url)
                if article:
                    articles.append(article)
                    logger.info(f"Artículo extraído exitosamente: {article.titulo[:60]}...")
            except Exception as e:
                logger.error(f"Error extrayendo artículo {url}: {e}", exc_info=True)
        
        logger.info(f"Scraping completado. Total de artículos extraídos: {len(articles)}")
        return articles
    
    def _extract_article_urls_from_section(self, section_url: str) -> set[str]:
        """
        Extrae URLs de artículos de una sección específica de Página 12.
        
        Args:
            section_url: URL de la sección a scrapear
            
        Returns:
            set[str]: Conjunto de URLs de artículos encontradas
        """
        try:
            response = self.session.get(section_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            article_urls = set()
            
            # Buscar enlaces en artículos
            # Página 12 usa structure con articles y divs
            articles = soup.find_all('article')
            for article in articles:
                links = article.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    
                    # Filtrar URLs no deseadas
                    if any(skip in href for skip in ['/autores/', '/tags/', '/suplementos/', 'javascript:', '#']):
                        continue
                    
                    # Convertir a URL absoluta
                    if href.startswith('/'):
                        href = urljoin(self.base_url, href)
                    elif not href.startswith('http'):
                        continue
                    
                    # Verificar que sea de Página 12 y que sea una nota
                    if 'pagina12.com.ar' in href and ('/notas/' in href or '/articulos/' in href):
                        article_urls.add(href)
            
            # También buscar en divs de noticias
            news_divs = soup.find_all('div', class_=['article-item', 'nota'])
            for div in news_divs:
                links = div.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    
                    if any(skip in href for skip in ['/autores/', '/tags/', '/suplementos/', 'javascript:', '#']):
                        continue
                    
                    if href.startswith('/'):
                        href = urljoin(self.base_url, href)
                    elif not href.startswith('http'):
                        continue
                    
                    if 'pagina12.com.ar' in href and ('/notas/' in href or '/articulos/' in href):
                        article_urls.add(href)
            
            return article_urls
            
        except requests.RequestException as e:
            logger.error(f"Error de red al acceder a {section_url}: {e}")
            return set()
        except Exception as e:
            logger.error(f"Error inesperado en {section_url}: {e}", exc_info=True)
            return set()
    
    def _extract_article_content(self, url: str) -> Optional[ArticleDTO]:
        """
        Extrae el contenido completo de un artículo individual.
        
        Args:
            url: URL del artículo a extraer
            
        Returns:
            Optional[ArticleDTO]: ArticleDTO con el contenido extraído o None si falla
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extraer título
            titulo = self._extract_title(soup)
            if not titulo:
                logger.warning(f"No se pudo extraer el título de {url}")
                return None
            
            # Extraer contenido
            contenido = self._extract_content(soup)
            if not contenido:
                logger.warning(f"No se pudo extraer el contenido de {url}")
                contenido = ""
            
            # Extraer fecha de publicación
            fecha_publicacion = self._extract_publication_date(soup)
            
            return ArticleDTO(
                titulo=titulo,
                url=url,
                contenido=contenido,
                fecha_publicacion=fecha_publicacion,
                fuente="Página 12"
            )
            
        except requests.RequestException as e:
            logger.error(f"Error de red al acceder al artículo {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado extrayendo artículo {url}: {e}", exc_info=True)
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae el título del artículo."""
        # Intentar diferentes selectores de título
        title_selectors = [
            ('h1', {'class': 'article-title'}),
            ('h1', {'class': 'titulo-nota'}),
            ('h1', {'class': 'title'}),
            ('h1', {}),
            ('meta', {'property': 'og:title'}),
        ]
        
        for tag, attrs in title_selectors:
            if tag == 'meta':
                element = soup.find(tag, attrs=attrs)
                if element and element.get('content'):
                    return self._clean_text(element['content'])
            else:
                element = soup.find(tag, attrs=attrs if attrs else None)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return self._clean_text(text)
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extrae el contenido del artículo."""
        content_parts = []
        
        # Buscar contenido en diferentes posibles contenedores
        content_selectors = [
            ('div', {'class': 'article-text'}),
            ('div', {'class': 'article-body'}),
            ('div', {'class': 'texto-nota'}),
            ('div', {'class': 'content-nota'}),
            ('article', {'class': 'article'}),
        ]
        
        for tag, attrs in content_selectors:
            container = soup.find(tag, attrs=attrs if attrs else None)
            if container:
                # Extraer todos los párrafos
                paragraphs = container.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # Filtrar párrafos muy cortos
                        content_parts.append(self._clean_text(text))
        
        # Si no se encontraron párrafos, intentar con el contenido completo del article
        if not content_parts:
            article = soup.find('article')
            if article:
                paragraphs = article.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        content_parts.append(self._clean_text(text))
        
        return ' '.join(content_parts)
    
    def _extract_publication_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extrae la fecha de publicación del artículo."""
        # Intentar extraer fecha de metadatos
        date_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'publishdate'}),
            ('meta', {'property': 'og:published_time'}),
            ('time', {'datetime': True}),
            ('span', {'class': 'date'}),
        ]
        
        for tag, attrs in date_selectors:
            element = soup.find(tag, attrs=attrs)
            if element:
                date_str = None
                if tag == 'meta':
                    date_str = element.get('content')
                elif tag == 'time':
                    date_str = element.get('datetime')
                elif tag == 'span':
                    date_str = element.get_text(strip=True)
                
                if date_str:
                    try:
                        # Intentar parsear la fecha
                        if 'T' in date_str:
                            # ISO format
                            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        else:
                            # Intentar otros formatos
                            return datetime.strptime(date_str, '%Y-%m-%d')
                    except (ValueError, AttributeError):
                        continue
        
        # Si no se encuentra fecha, usar la fecha actual
        return datetime.now(timezone.utc)
    
    def _clean_text(self, text: str) -> str:
        """
        Limpia y normaliza el texto extraído.
        Reutiliza la lógica de validación y limpieza del scraper de Clarín.
        
        Args:
            text: Texto a limpiar
            
        Returns:
            str: Texto limpio y normalizado
        """
        if not text:
            return ""
        
        # Eliminar espacios múltiples
        text = ' '.join(text.split())
        
        # Eliminar saltos de línea y caracteres especiales
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Eliminar espacios múltiples resultantes
        text = ' '.join(text.split())
        
        return text.strip()
    
    def __del__(self):
        """Cerrar la sesión al destruir el objeto."""
        if hasattr(self, 'session'):
            self.session.close()

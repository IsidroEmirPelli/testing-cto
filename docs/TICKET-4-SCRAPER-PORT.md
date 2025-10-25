# Ticket 4: Interfaz Base de Scraping (ScraperPort) y ArticleDTO

## Descripción

Este ticket implementa la interfaz base de scraping que estandariza cómo todos los scrapers interactúan con el sistema, junto con el DTO común para artículos scrapeados.

## Componentes Implementados

### 1. ScraperPort (Protocol)

**Ubicación:** `src/domain/ports/scraper_port.py`

Interfaz basada en `typing.Protocol` que define el contrato para todos los scrapers del sistema.

```python
from typing import Protocol
from src.domain.dto.article_dto import ArticleDTO

class ScraperPort(Protocol):
    def scrape(self) -> list[ArticleDTO]:
        """
        Extrae artículos de una fuente de noticias.
        
        Returns:
            list[ArticleDTO]: Lista de artículos extraídos en formato estandarizado
        """
        ...
```

#### Ventajas del uso de Protocol

- **Tipado estructural:** No requiere herencia explícita
- **Duck typing con type hints:** Cualquier clase con el método `scrape()` correcto es compatible
- **Flexibilidad:** Permite implementaciones independientes sin acoplamiento a una clase base

#### Ejemplo de Implementación

```python
from src.domain.dto.article_dto import ArticleDTO
from src.domain.ports.scraper_port import ScraperPort

class ClarinScraper:
    """Scraper específico para el diario Clarín."""
    
    def scrape(self) -> list[ArticleDTO]:
        articles = []
        # Lógica específica de scraping para Clarín
        # ...
        return articles

# El type checker reconoce automáticamente que ClarinScraper
# es compatible con ScraperPort sin herencia explícita
scraper: ScraperPort = ClarinScraper()
```

### 2. ArticleDTO

**Ubicación:** `src/domain/dto/article_dto.py`

DTO basado en Pydantic que representa el formato común de un artículo scrapeado, independientemente de la fuente.

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ArticleDTO(BaseModel):
    titulo: str
    url: str
    contenido: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None
    fuente: str
```

#### Características

- **Validación automática:** Pydantic valida tipos y campos requeridos
- **Serialización JSON:** Métodos `model_dump()` y `model_dump_json()` integrados
- **Deserialización JSON:** Método `model_validate_json()` para parsear JSON
- **Campos opcionales:** `contenido` y `fecha_publicacion` pueden ser `None`
- **Inmutabilidad:** Por defecto, los modelos Pydantic son inmutables (puede configurarse)

#### Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `titulo` | `str` | Sí | Título del artículo |
| `url` | `str` | Sí | URL del artículo original |
| `contenido` | `Optional[str]` | No | Contenido completo del artículo |
| `fecha_publicacion` | `Optional[datetime]` | No | Fecha de publicación del artículo |
| `fuente` | `str` | Sí | Nombre de la fuente (ej: "Clarín", "Página 12") |

#### Ejemplo de Uso

```python
from datetime import datetime
from src.domain.dto.article_dto import ArticleDTO

# Crear un artículo con todos los campos
article = ArticleDTO(
    titulo="Ejemplo de noticia",
    url="https://www.clarin.com/ejemplo",
    contenido="Este es el contenido completo...",
    fecha_publicacion=datetime(2024, 1, 15, 10, 30),
    fuente="Clarín"
)

# Crear un artículo con campos opcionales en None
article_minimal = ArticleDTO(
    titulo="Noticia sin contenido",
    url="https://ejemplo.com/noticia",
    fuente="La Nación"
)

# Serializar a JSON
json_data = article.model_dump_json()

# Deserializar desde JSON
article_from_json = ArticleDTO.model_validate_json(json_data)

# Convertir a diccionario
article_dict = article.model_dump()
```

## Integración con Scrapers Existentes

Los scrapers específicos de cada fuente deberán:

1. Implementar el método `scrape() -> list[ArticleDTO]`
2. Retornar una lista de objetos `ArticleDTO` con los datos extraídos
3. Manejar errores apropiadamente

### Ejemplo: Implementar un nuevo scraper

```python
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.domain.dto.article_dto import ArticleDTO
from src.domain.ports.scraper_port import ScraperPort

class Pagina12Scraper:
    """Scraper para el diario Página 12."""
    
    def __init__(self, base_url: str = "https://www.pagina12.com.ar"):
        self.base_url = base_url
    
    def scrape(self) -> list[ArticleDTO]:
        """Extrae artículos de Página 12."""
        articles = []
        
        try:
            # Obtener la página principal
            response = requests.get(self.base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer artículos (ejemplo simplificado)
            for article_elem in soup.select('.article-item'):
                titulo = article_elem.select_one('.title').text.strip()
                url = article_elem.select_one('a')['href']
                
                # Crear ArticleDTO
                article = ArticleDTO(
                    titulo=titulo,
                    url=url,
                    fuente="Página 12"
                )
                articles.append(article)
        
        except Exception as e:
            # Manejar errores apropiadamente
            print(f"Error scraping Página 12: {e}")
        
        return articles

# Uso
scraper: ScraperPort = Pagina12Scraper()
articles = scraper.scrape()
```

## Coordinador de Scrapers

Con esta interfaz estandarizada, es posible crear un coordinador que orqueste múltiples scrapers:

```python
from typing import List
from src.domain.dto.article_dto import ArticleDTO
from src.domain.ports.scraper_port import ScraperPort

class ScraperCoordinator:
    """Coordina la ejecución de múltiples scrapers."""
    
    def __init__(self, scrapers: List[ScraperPort]):
        self.scrapers = scrapers
    
    def scrape_all(self) -> list[ArticleDTO]:
        """Ejecuta todos los scrapers y combina los resultados."""
        all_articles = []
        
        for scraper in self.scrapers:
            try:
                articles = scraper.scrape()
                all_articles.extend(articles)
            except Exception as e:
                print(f"Error en scraper {scraper.__class__.__name__}: {e}")
        
        return all_articles

# Uso
coordinator = ScraperCoordinator([
    ClarinScraper(),
    Pagina12Scraper(),
    LaNacionScraper()
])
all_articles = coordinator.scrape_all()
```

## Compatibilidad con Código Existente

La interfaz anterior `IScraperPort` (basada en ABC) se mantiene por compatibilidad, pero está marcada como legacy en la documentación. Los nuevos scrapers deberían usar `ScraperPort` (Protocol).

```python
# Legacy (mantener por compatibilidad)
class IScraperPort(ABC):
    @abstractmethod
    def scrape_sources(self, sources: List[str]) -> List[NewsArticle]:
        pass

# Nuevo (recomendado)
class ScraperPort(Protocol):
    def scrape(self) -> list[ArticleDTO]:
        ...
```

## Testing

### Test de ArticleDTO

```python
from datetime import datetime
from src.domain.dto.article_dto import ArticleDTO

def test_article_dto_creation():
    article = ArticleDTO(
        titulo="Test",
        url="https://test.com",
        contenido="Contenido de prueba",
        fecha_publicacion=datetime.now(),
        fuente="Test Source"
    )
    assert article.titulo == "Test"
    assert article.url == "https://test.com"

def test_article_dto_optional_fields():
    article = ArticleDTO(
        titulo="Test",
        url="https://test.com",
        fuente="Test Source"
    )
    assert article.contenido is None
    assert article.fecha_publicacion is None

def test_article_dto_validation():
    with pytest.raises(ValidationError):
        ArticleDTO(titulo="Missing url", fuente="Test")
```

### Test de ScraperPort

```python
from src.domain.dto.article_dto import ArticleDTO
from src.domain.ports.scraper_port import ScraperPort

def test_scraper_port_protocol():
    class TestScraper:
        def scrape(self) -> list[ArticleDTO]:
            return [
                ArticleDTO(
                    titulo="Test",
                    url="https://test.com",
                    fuente="Test"
                )
            ]
    
    scraper: ScraperPort = TestScraper()
    articles = scraper.scrape()
    assert len(articles) == 1
    assert isinstance(articles[0], ArticleDTO)
```

## Próximos Pasos

1. Implementar scrapers específicos para cada fuente (Clarín, La Nación, Página 12, etc.)
2. Crear el coordinador de scrapers
3. Integrar con el sistema de colas para procesamiento asíncrono
4. Implementar manejo de errores y reintentos
5. Agregar métricas y logging

## Dependencias Agregadas

- `pydantic==2.5.3` agregado a `requirements.txt`

## Estructura de Archivos

```
src/
├── domain/
│   ├── dto/
│   │   ├── __init__.py          # Exporta ArticleDTO
│   │   └── article_dto.py       # DTO para artículos scrapeados
│   └── ports/
│       ├── __init__.py          # Exporta IScraperPort y ScraperPort
│       └── scraper_port.py      # Interfaces de scraper (legacy y nueva)
```

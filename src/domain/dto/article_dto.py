from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ArticleDTO(BaseModel):
    """
    Data Transfer Object para artículos scrapeados.

    Este DTO representa la estructura común de un artículo obtenido por cualquier scraper,
    independientemente de la fuente (Clarín, Página 12, La Nación, etc.).

    Attributes:
        titulo: Título del artículo
        url: URL del artículo original
        contenido: Contenido completo del artículo (opcional si no se pudo extraer)
        fecha_publicacion: Fecha de publicación del artículo (opcional si no está disponible)
        fuente: Nombre de la fuente del artículo (ej: "Clarín", "Página 12")
    """

    titulo: str = Field(..., description="Título del artículo")
    url: str = Field(..., description="URL del artículo original")
    contenido: Optional[str] = Field(
        None, description="Contenido completo del artículo"
    )
    fecha_publicacion: Optional[datetime] = Field(
        None, description="Fecha de publicación del artículo"
    )
    fuente: str = Field(
        ..., description="Nombre de la fuente (ej: 'Clarín', 'Página 12')"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "titulo": "Ejemplo de noticia",
                    "url": "https://www.clarin.com/ejemplo-noticia",
                    "contenido": "Este es el contenido completo de la noticia...",
                    "fecha_publicacion": "2024-01-15T10:30:00",
                    "fuente": "Clarín",
                }
            ]
        }
    }

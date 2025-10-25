from enum import Enum, auto


class NewsSource(Enum):
    """
    Enumeración de fuentes de noticias disponibles.

    Cada fuente incluye:
    - Un identificador único generado con auto()
    - Un nombre descriptivo
    - El dominio del sitio web
    - El país de origen
    """

    CLARIN = auto()
    LA_NACION = auto()
    PAGINA12 = auto()
    INFOBAE = auto()

    @property
    def nombre(self) -> str:
        """Devuelve el nombre legible de la fuente."""
        nombres = {
            NewsSource.CLARIN: "Clarín",
            NewsSource.LA_NACION: "La Nación",
            NewsSource.PAGINA12: "Página 12",
            NewsSource.INFOBAE: "Infobae",
        }
        return nombres[self]

    @property
    def dominio(self) -> str:
        """Devuelve el dominio de la fuente."""
        dominios = {
            NewsSource.CLARIN: "www.clarin.com",
            NewsSource.LA_NACION: "www.lanacion.com.ar",
            NewsSource.PAGINA12: "www.pagina12.com.ar",
            NewsSource.INFOBAE: "www.infobae.com",
        }
        return dominios[self]

    @property
    def pais(self) -> str:
        """Devuelve el país de la fuente."""
        return "Argentina"

    @classmethod
    def from_nombre(cls, nombre: str) -> "NewsSource":
        """
        Obtiene la fuente por su nombre.

        Args:
            nombre: Nombre de la fuente (case-insensitive)

        Returns:
            NewsSource correspondiente

        Raises:
            ValueError: Si no se encuentra la fuente
        """
        nombre_lower = nombre.lower().strip()
        for source in cls:
            if source.nombre.lower() == nombre_lower:
                return source
        raise ValueError(f"Fuente no encontrada: {nombre}")

    @classmethod
    def from_dominio(cls, dominio: str) -> "NewsSource":
        """
        Obtiene la fuente por su dominio.

        Args:
            dominio: Dominio de la fuente

        Returns:
            NewsSource correspondiente

        Raises:
            ValueError: Si no se encuentra la fuente
        """
        dominio_clean = (
            dominio.lower()
            .strip()
            .replace("https://", "")
            .replace("http://", "")
            .rstrip("/")
        )
        for source in cls:
            if (
                source.dominio.lower() in dominio_clean
                or dominio_clean in source.dominio.lower()
            ):
                return source
        raise ValueError(f"Fuente no encontrada para dominio: {dominio}")

    @classmethod
    def all_sources(cls) -> list["NewsSource"]:
        """Devuelve todas las fuentes disponibles."""
        return list(cls)

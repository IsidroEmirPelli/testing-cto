import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class TextCleaningPipeline:
    def process_item(self, item, spider):
        if "titulo" in item and item["titulo"]:
            item["titulo"] = self._clean_text(item["titulo"])

        if "contenido" in item and item["contenido"]:
            item["contenido"] = self._clean_html_content(item["contenido"])

        logger.info(
            f"Artículo limpio: {item['titulo'][:50]}... - Fuente: {item['fuente']}"
        )
        return item

    def _clean_html_content(self, html_content):
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, "lxml")

        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        text = soup.get_text(separator=" ", strip=True)

        text = self._clean_text(text)

        return text

    def _clean_text(self, text):
        if not text:
            return ""

        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        text = text.replace("\xa0", " ")
        text = text.replace("\u200b", "")

        return text


class ValidationPipeline:
    def process_item(self, item, spider):
        required_fields = ["titulo", "contenido", "fuente", "url"]

        for field in required_fields:
            if not item.get(field):
                logger.warning(f"Item descartado - Campo requerido faltante: {field}")
                raise Exception(f"Campo requerido faltante: {field}")

        if len(item["contenido"]) < 100:
            logger.warning(f"Item descartado - Contenido muy corto: {item['url']}")
            raise Exception("Contenido demasiado corto")

        return item

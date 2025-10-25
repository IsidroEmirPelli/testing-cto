import scrapy


class NewsArticleItem(scrapy.Item):
    titulo = scrapy.Field()
    contenido = scrapy.Field()
    fuente = scrapy.Field()
    fecha_publicacion = scrapy.Field()
    url = scrapy.Field()
    categoria = scrapy.Field()

from src.application.dto.news_article_dto import (
    CreateNewsArticleDTO,
    NewsArticleDTO,
    UpdateNewsArticleDTO,
)
from src.application.dto.scraping_job_dto import (
    CreateScrapingJobDTO,
    ScrapingJobDTO,
)
from src.application.dto.source_dto import CreateSourceDTO, SourceDTO, UpdateSourceDTO
from src.application.dto.user_dto import CreateUserDTO, UpdateUserDTO, UserDTO

__all__ = [
    "UserDTO",
    "CreateUserDTO",
    "UpdateUserDTO",
    "NewsArticleDTO",
    "CreateNewsArticleDTO",
    "UpdateNewsArticleDTO",
    "SourceDTO",
    "CreateSourceDTO",
    "UpdateSourceDTO",
    "ScrapingJobDTO",
    "CreateScrapingJobDTO",
]

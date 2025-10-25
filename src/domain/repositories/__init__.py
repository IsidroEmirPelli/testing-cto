from src.domain.repositories.news_article_repository import NewsArticleRepository
from src.domain.repositories.scraping_job_repository import ScrapingJobRepository
from src.domain.repositories.source_repository import SourceRepository
from src.domain.repositories.user_repository import UserRepository

__all__ = [
    "UserRepository",
    "NewsArticleRepository",
    "SourceRepository",
    "ScrapingJobRepository",
]

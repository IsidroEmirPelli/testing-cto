import uvicorn

from src.infrastructure.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.presentation.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

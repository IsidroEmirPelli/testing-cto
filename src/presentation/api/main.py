from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config.settings import settings
from src.presentation.api.routes import health, users

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI application with Hexagonal Architecture",
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI Hexagonal Architecture",
        "docs": "/docs",
        "redoc": "/redoc"
    }

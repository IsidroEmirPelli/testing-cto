import pytest

from src.application.dto.user_dto import CreateUserDTO
from src.application.use_cases.create_user import CreateUserUseCase
from src.infrastructure.persistence.in_memory_user_repository import (
    InMemoryUserRepository,
)


@pytest.mark.asyncio
async def test_create_user_success():
    repository = InMemoryUserRepository()
    use_case = CreateUserUseCase(repository)
    dto = CreateUserDTO(email="test@example.com", name="Test User")

    result = await use_case.execute(dto)

    assert result.email == dto.email
    assert result.name == dto.name
    assert result.is_active is True
    assert result.id is not None


@pytest.mark.asyncio
async def test_create_user_duplicate_email():
    repository = InMemoryUserRepository()
    use_case = CreateUserUseCase(repository)
    dto = CreateUserDTO(email="test@example.com", name="Test User")

    await use_case.execute(dto)

    with pytest.raises(ValueError, match="already exists"):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_create_user_invalid_email():
    repository = InMemoryUserRepository()
    use_case = CreateUserUseCase(repository)
    dto = CreateUserDTO(email="invalid-email", name="Test User")

    with pytest.raises(ValueError, match="Invalid email format"):
        await use_case.execute(dto)

from functools import lru_cache

from src.application.use_cases.create_user import CreateUserUseCase
from src.application.use_cases.delete_user import DeleteUserUseCase
from src.application.use_cases.get_user import GetUserUseCase
from src.application.use_cases.list_users import ListUsersUseCase
from src.application.use_cases.update_user import UpdateUserUseCase
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository


@lru_cache()
def get_user_repository() -> UserRepository:
    return InMemoryUserRepository()


def get_create_user_use_case() -> CreateUserUseCase:
    return CreateUserUseCase(get_user_repository())


def get_get_user_use_case() -> GetUserUseCase:
    return GetUserUseCase(get_user_repository())


def get_list_users_use_case() -> ListUsersUseCase:
    return ListUsersUseCase(get_user_repository())


def get_update_user_use_case() -> UpdateUserUseCase:
    return UpdateUserUseCase(get_user_repository())


def get_delete_user_use_case() -> DeleteUserUseCase:
    return DeleteUserUseCase(get_user_repository())

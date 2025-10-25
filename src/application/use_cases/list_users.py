from typing import List

from src.application.dto.user_dto import UserDTO
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class ListUsersUseCase:

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[UserDTO]:
        users = await self._user_repository.get_all(skip=skip, limit=limit)
        return [self._to_dto(user) for user in users]

    @staticmethod
    def _to_dto(user: User) -> UserDTO:
        return UserDTO(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_active=user.is_active,
        )

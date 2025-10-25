from typing import Optional
from uuid import UUID

from src.application.dto.user_dto import UserDTO
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class GetUserUseCase:
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self, user_id: UUID) -> Optional[UserDTO]:
        user = await self._user_repository.get_by_id(user_id)
        
        if not user:
            return None

        return self._to_dto(user)

    @staticmethod
    def _to_dto(user: User) -> UserDTO:
        return UserDTO(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_active=user.is_active
        )

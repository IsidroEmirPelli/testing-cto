from uuid import UUID

from src.application.dto.user_dto import UpdateUserDTO, UserDTO
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class UpdateUserUseCase:
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self, user_id: UUID, dto: UpdateUserDTO) -> UserDTO:
        user = await self._user_repository.get_by_id(user_id)
        
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        if dto.name:
            user.update_name(dto.name)

        updated_user = await self._user_repository.update(user)
        return self._to_dto(updated_user)

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

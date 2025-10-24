from uuid import UUID

from src.domain.repositories.user_repository import UserRepository


class DeleteUserUseCase:
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self, user_id: UUID) -> bool:
        user = await self._user_repository.get_by_id(user_id)
        
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        return await self._user_repository.delete(user_id)

from src.application.dto.user_dto import CreateUserDTO, UserDTO
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.email import Email


class CreateUserUseCase:
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self, dto: CreateUserDTO) -> UserDTO:
        email = Email(dto.email)
        
        existing_user = await self._user_repository.get_by_email(str(email))
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        user = User.create(email=str(email), name=dto.name)
        created_user = await self._user_repository.create(user)

        return self._to_dto(created_user)

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

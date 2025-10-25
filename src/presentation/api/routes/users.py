from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dto.user_dto import CreateUserDTO, UpdateUserDTO
from src.application.use_cases.create_user import CreateUserUseCase
from src.application.use_cases.delete_user import DeleteUserUseCase
from src.application.use_cases.get_user import GetUserUseCase
from src.application.use_cases.list_users import ListUsersUseCase
from src.application.use_cases.update_user import UpdateUserUseCase
from src.presentation.api.dependencies import (
    get_create_user_use_case,
    get_delete_user_use_case,
    get_get_user_use_case,
    get_list_users_use_case,
    get_update_user_use_case,
)
from src.presentation.schemas.user_schema import (
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    user_data: UserCreateSchema,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    try:
        dto = CreateUserDTO(email=user_data.email, name=user_data.name)
        user = await use_case.execute(dto)
        return UserResponseSchema(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_active=user.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponseSchema, summary="Get user by ID")
async def get_user(
    user_id: UUID, use_case: GetUserUseCase = Depends(get_get_user_use_case)
):
    user = await use_case.execute(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return UserResponseSchema(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_active=user.is_active,
    )


@router.get("", response_model=List[UserResponseSchema], summary="List all users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
):
    users = await use_case.execute(skip=skip, limit=limit)
    return [
        UserResponseSchema(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_active=user.is_active,
        )
        for user in users
    ]


@router.put("/{user_id}", response_model=UserResponseSchema, summary="Update user")
async def update_user(
    user_id: UUID,
    user_data: UserUpdateSchema,
    use_case: UpdateUserUseCase = Depends(get_update_user_use_case),
):
    try:
        dto = UpdateUserDTO(name=user_data.name)
        user = await use_case.execute(user_id, dto)
        return UserResponseSchema(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_active=user.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user"
)
async def delete_user(
    user_id: UUID, use_case: DeleteUserUseCase = Depends(get_delete_user_use_case)
):
    try:
        await use_case.execute(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

from datetime import datetime
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from containers import Container
from database import get_db
from user.application.user_service import UserService

router = InferringRouter(prefix="/users")


class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)


class UpdateUserBody(BaseModel):
    name: str | None = Field(min_length=2, max_length=32, default=None)
    password: str | None = Field(min_length=8, max_length=32, default=None)


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime


class GetUsersResponse(BaseModel):
    total_count: int
    page: int
    users: list[UserResponse]


@cbv(router)
class UserRouter:
    @inject
    def __init__(self, user_service: Annotated[UserService, Depends(Provide[Container.user_service])]):
        self.user_service = user_service

    # POST /users/ - 회원 등록
    @router.post("/", status_code=201, response_model=UserResponse)
    def create_user(self, session: Annotated[Session, Depends(get_db)], user: CreateUserBody) -> UserResponse:
        # 인터페이스 계층은 애플리케이션 계층에 의존해도 됨
        created_user = self.user_service.create_user(
            session=session,
            name=user.name,
            email=user.email,
            password=user.password,
        )

        return UserResponse(
            id=created_user.id,
            name=created_user.name,
            email=created_user.email,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
        )

    # GET /users/ - 이메일로 회원 조회
    @router.get("/", status_code=200, response_model=UserResponse)
    def get_user(self, session: Annotated[Session, Depends(get_db)], email: str) -> UserResponse:
        user = self.user_service.get_user(
            session=session,
            email=email,
        )

        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    # GET /users/list - 회원 목록 조회
    @router.get("/list", status_code=200, response_model=GetUsersResponse)
    def get_users(
        self, session: Annotated[Session, Depends(get_db)], page: int = 1, items_per_page: int = 10
    ) -> GetUsersResponse:
        total_count, users = self.user_service.get_users(session=session, page=page, items_per_page=items_per_page)

        return GetUsersResponse(
            total_count=total_count,
            page=page,
            users=[
                UserResponse(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )
                for user in users
            ],
        )

    # PUT /users/{user_id} - 회원 정보 업데이트
    @router.put("/{user_id}", status_code=200, response_model=UserResponse)
    def update_user(
        self, session: Annotated[Session, Depends(get_db)], user_id: str, user: UpdateUserBody
    ) -> UserResponse:
        updated_user = self.user_service.update_user(
            session=session,
            user_id=user_id,
            name=user.name,
            password=user.password,
        )

        return UserResponse(
            id=updated_user.id,
            name=updated_user.name,
            email=updated_user.email,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )

    # DELETE /users/{user_id} - 회원 탈퇴
    @router.delete("/{user_id}", status_code=204)
    def delete_user(self, session: Annotated[Session, Depends(get_db)], user_id: str) -> None:
        self.user_service.delete_user(
            session=session,
            user_id=user_id,
        )

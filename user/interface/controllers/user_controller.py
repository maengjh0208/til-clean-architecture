from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session

from containers import Container
from database import get_db
from user.application.user_service import UserService

router = InferringRouter(prefix="/users")


class CreateUserBody(BaseModel):
    name: str
    email: str
    password: str


class UpdateUserBody(BaseModel):
    name: str | None = None
    password: str | None = None


@cbv(router)
class UserRouter:
    @inject
    def __init__(self, user_service: Annotated[UserService, Depends(Provide[Container.user_service])]):
        self.user_service = user_service

    # POST /users/ - 회원 등록
    @router.post("/", status_code=201)
    def create_user(self, session: Annotated[Session, Depends(get_db)], user: CreateUserBody):
        # 인터페이스 계층은 애플리케이션 계층에 의존해도 됨
        created_user = self.user_service.create_user(
            session=session,
            name=user.name,
            email=user.email,
            password=user.password,
        )

        return created_user

    # GET /users/ - 이메일로 회원 조회
    @router.get("/", status_code=200)
    def get_user(self, session: Annotated[Session, Depends(get_db)], email: str):
        user = self.user_service.get_user(
            session=session,
            email=email,
        )

        return user

    # GET /users/list - 유저 목록 조회
    @router.get("/list", status_code=200)
    def get_users(self, session: Annotated[Session, Depends(get_db)], page: int = 1, items_per_page: int = 10):
        total_count, users = self.user_service.get_users(session=session, page=page, items_per_page=items_per_page)

        return {"total_count": total_count, "page": page, "users": users}

    # PUT /users/{user_id} - 유저 정보 업데이트
    @router.put("/{user_id}", status_code=200)
    def update_user(self, session: Annotated[Session, Depends(get_db)], user_id: str, user: UpdateUserBody):
        updated_user = self.user_service.update_user(
            session=session,
            user_id=user_id,
            name=user.name,
            password=user.password,
        )

        return updated_user

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
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


class GetUsersResponse(BaseModel):
    total_count: int
    page: int
    users: list[UserResponse]


@cbv(router)
class UserRouter:
    # 의존성 객체를 사용하는 함수에 @inject 데코레이터를 명시해 주입받은 객체를 사용한다고 선언한다.
    # @inject 를 사용하지 않아도 dependency-injector 는 메서드의 매개변수를 검사하고 필요한 의존성을 주입할 수 있다.
    # 다만, @inject 를 사용하면 해당 메서드가 의존성 주입을 위해 디자인 되었음을 코드에서 명시적으로 확인할 수 있다.
    # 코드의 가독성과 유지보수성을 고려해 @injet 를 사용하는 것이 권장된다.
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
        )

    # DELETE /users/{user_id} - 회원 탈퇴
    @router.delete("/{user_id}", status_code=204)
    def delete_user(self, session: Annotated[Session, Depends(get_db)], user_id: str) -> None:
        self.user_service.delete_user(
            session=session,
            user_id=user_id,
        )

    # POST /users/login - 로그인
    @router.post("/login")
    def login(
        self,
        session: Annotated[Session, Depends(get_db)],
        # 데이터 형식은 username 과 password 로 고정되어 있다. OAuth2 스펙에 정해진 이름이다.
        # OAuth2 는 주고받는 방식이고 (form 으로 받아서 토큰을 발급한다), JWT 는 토큰 형식이다.
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ):
        access_token = self.user_service.login(
            session=session,
            email=form_data.username,
            password=form_data.password,
        )

        return {"access_token": access_token, "token_type": "bearer"}

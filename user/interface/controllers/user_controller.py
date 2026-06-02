from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from pydantic import BaseModel

from user.application.user_service import UserService

router = InferringRouter(prefix="/users")


class CreateUserBody(BaseModel):
    name: str
    email: str
    password: str


@cbv(router)
class UserRouter:
    def __init__(self):
        self.user_service = UserService()

    # POST /users/ - 회원 등록
    @router.post("/", status_code=201)
    def create_user(self, user: CreateUserBody):
        # 인터페이스 계층은 애플리케이션 계층에 의존해도 됨
        created_user = self.user_service.create_user(
            name=user.name,
            email=user.email,
            password=user.password,
        )

        return created_user

    # GET /users/ - 회원 조회
    @router.get("/", status_code=200)
    def get_user(self, email: str):
        user = self.user_service.get_user(
            email=email,
        )

        return user

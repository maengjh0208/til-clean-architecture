from datetime import datetime

from dependency_injector.wiring import inject
from fastapi import HTTPException
from ulid import ULID

from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User
from utils.crypto import Crypto


class UserService:
    # 의존성 객체를 사용하는 함수에 @inject 데코레이터를 명시해 주입받은 객체를 사용한다고 선언한다.
    # @inject 를 사용하지 않아도 dependency-injector 는 메서드의 매개변수를 검사하고 필요한 의존성을 주입할 수 있다.
    # 다만, @inject 를 사용하면 해당 메서드가 의존성 주입을 위해 디자인 되었음을 코드에서 명시적으로 확인할 수 있다.
    # 코드의 가독성과 유지보수성을 고려해 @injet 를 사용하는 것이 권장된다.
    @inject
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
        self.ulid = ULID()
        self.crypto = Crypto()

    def create_user(self, name: str, email: str, password: str) -> User:
        _user = None

        try:
            _user = self.user_repo.find_by_email(email)
        except HTTPException as e:
            if e.status_code != 422:
                raise e

        if _user:
            raise HTTPException(status_code=422)

        now = datetime.now()
        user: User = User(
            id=self.ulid.generate(),
            name=name,
            email=email,
            password=self.crypto.encrypt(password),
            created_at=now,
            updated_at=now,
        )
        self.user_repo.save(user)

        return user

    def get_user(self, email: str) -> User:
        user = self.user_repo.find_by_email(email)

        if not user:
            raise HTTPException(status_code=404)

        return user

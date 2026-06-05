from dependency_injector.wiring import inject
from fastapi import HTTPException
from sqlalchemy.orm import Session
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

    def create_user(self, session: Session, name: str, email: str, password: str, memo: str | None = None) -> User:
        _user = None

        try:
            _user = self.user_repo.find_by_email(session, email)
        except HTTPException as e:
            if e.status_code != 422:
                raise e

        if _user:
            raise HTTPException(status_code=422)

        user = User(
            id=self.ulid.generate(),
            name=name,
            email=email,
            password=self.crypto.encrypt(password),
            memo=memo,
        )
        self.user_repo.save(session, user)

        return user

    def get_user(self, session: Session, email: str) -> User:
        user = self.user_repo.find_by_email(session, email)

        if not user:
            raise HTTPException(status_code=404)

        return user

    def get_users(self, session: Session, page: int, items_per_page: int) -> tuple[int, list[User]]:
        total_count, users = self.user_repo.get_users(session, page, items_per_page)

        return total_count, users

    def update_user(self, session: Session, user_id: str, name: str | None = None, password: str | None = None) -> User:
        user = self.user_repo.find_by_id(session, user_id)

        if not user:
            raise HTTPException(status_code=404)

        if name:
            user.name = name
        if password:
            user.password = self.crypto.encrypt(password)

        self.user_repo.update_user(session, user)

        return user

    def delete_user(self, session: Session, user_id: str) -> None:
        if not self.user_repo.find_by_id(session, user_id):
            raise HTTPException(status_code=404)

        self.user_repo.delete(session, user_id)

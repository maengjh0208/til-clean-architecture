from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ulid import ULID

from common.auth import Role, create_access_token
from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User
from utils.crypto import Crypto


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
        self.ulid = ULID()
        self.crypto = Crypto()

    def create_user(
        self,
        session: Session,
        name: str,
        email: str,
        password: str,
        memo: str | None = None,
    ) -> User:
        _user = None

        try:
            _user = self.user_repo.find_by_email(session, email)
        except HTTPException as e:
            if e.status_code != status.HTTP_422_UNPROCESSABLE_CONTENT:
                raise e

        if _user:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)

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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return user

    def get_users(self, session: Session, page: int, items_per_page: int) -> tuple[int, list[User]]:
        total_count, users = self.user_repo.get_users(session, page, items_per_page)

        return total_count, users

    def update_user(
        self,
        session: Session,
        user_id: str,
        name: str | None = None,
        password: str | None = None,
    ) -> User:
        user = self.user_repo.find_by_id(session, user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if name:
            user.name = name
        if password:
            user.password = self.crypto.encrypt(password)

        self.user_repo.update_user(session, user)

        return user

    def delete_user(self, session: Session, user_id: str) -> None:
        if not self.user_repo.find_by_id(session, user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        self.user_repo.delete(session, user_id)

    def login(self, session: Session, email: str, password: str) -> str:
        user = self.user_repo.find_by_email(session, email)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if not self.crypto.verify(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        access_token = create_access_token(
            payload={"user_id": user.id},
            role=Role.USER,
        )

        return access_token

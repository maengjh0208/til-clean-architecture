from abc import ABCMeta, abstractmethod

from sqlalchemy.orm import Session

from user.domain.user import User


# class IUserRepository(ABC) 과 동일하다.
class IUserRepository(metaclass=ABCMeta):
    @abstractmethod
    # 타입힌트를 sqlalchemy 의 Session 으로 했는데, 원칙상 domain 계층은 infra 계층을 몰라야 하지만.. (sqlalchemy 는 infra 계층에서 알아야 하는 애)
    # 완벽한 분리보다는 실용성을 위해서 사용했음
    def save(self, session: Session, user: User) -> None:
        pass

    @abstractmethod
    def find_by_email(self, session: Session, email: str) -> User | None:
        """
        이메일로 유저를 검색한다.
        검색한 유저가 없을 경우 422 에러를 발생시킨다.
        """
        pass

    @abstractmethod
    def find_by_id(self, session: Session, id: str) -> User | None:
        pass

    @abstractmethod
    def update_user(self, session: Session, user: User) -> None:
        pass

    @abstractmethod
    def get_users(self, session: Session, page: int, items_per_page: int) -> tuple[int, list[User]]:
        pass

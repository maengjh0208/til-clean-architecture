from abc import ABCMeta, abstractmethod

from user.domain.user import User


# class IUserRepository(ABC) 과 동일하다.
class IUserRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, user: User):
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> User:
        """
        이메일로 유저를 검색한다.
        검색한 유저가 없을 경우 422 에러를 발생시킨다.
        """
        pass

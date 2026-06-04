from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User as UserVO
from user.infra.db_models.users import User


class UserRepository(IUserRepository):
    def save(self, session: Session, user: UserVO) -> None:
        new_user = User(
            id=user.id,
            name=user.name,
            email=user.email,
            password=user.password,
            memo=user.memo,
        )

        session.add(new_user)

    def find_by_email(self, session: Session, email: str) -> UserVO | None:
        query = select(
            User.id,
            User.name,
            User.email,
            User.password,
            User.memo,
            User.created_at,
            User.updated_at,
        ).where(User.email == email)

        user = session.execute(query).one_or_none()

        # DB 조회 결과를 그대로 넘기게 되면 SQLAlchemy 모델 객체가 서비스나 컨트롤러까지 흘러간다.
        # 그렇게 되면 인프라 계층(DB)을 서비스(Application)/컨트롤러(Interface)가 알게 된다.
        # 나중에 MySQL 을 MongoDB 로 바꾼다던지, ORM 을 교체한다던지 하면 서비스/컨트롤러까지 손대야 한다.
        # 변환을 infra 계층에서 끊어주면 infra 계층에서 바뀌어도 그 위 계층은 영향받지 않는다.
        # 의존 방향 : infra -> interface(컨트롤러) -> application(서비스) -> domain
        return (
            UserVO(
                id=user.id,
                name=user.name,
                email=user.email,
                password=user.password,
                memo=user.memo,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            if user
            else None
        )

    def find_by_id(self, session: Session, id: str) -> UserVO | None:
        query = select(
            User.id,
            User.name,
            User.email,
            User.password,
            User.memo,
            User.created_at,
            User.updated_at,
        ).where(User.id == id)

        user = session.execute(query).one_or_none()

        return (
            UserVO(
                id=user.id,
                name=user.name,
                email=user.email,
                password=user.password,
                memo=user.memo,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            if user
            else None
        )

    def update_user(self, session: Session, user_vo: UserVO) -> None:
        query = select(User).where(User.id == user_vo.id)
        user = session.execute(query).scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404)

        user.name = user_vo.name
        user.password = user_vo.password
        user.updated_at = user_vo.updated_at

    def get_users(self, session: Session, page: int, items_per_page: int) -> tuple[int, list[UserVO]]:
        query = select(func.count()).select_from(User)
        total_count = session.execute(query).scalar()

        offset = (page - 1) * items_per_page

        query = (
            select(
                User.id,
                User.name,
                User.email,
                User.password,
                User.memo,
                User.created_at,
                User.updated_at,
            )
            .offset(offset)
            .limit(items_per_page)
        )

        users = session.execute(query).all()

        return total_count, [
            UserVO(
                id=user.id,
                name=user.name,
                email=user.email,
                password=user.password,
                memo=user.memo,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user in users
        ]

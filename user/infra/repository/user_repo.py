from sqlalchemy import select

from database import SessionLocal
from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User as UserVO
from user.infra.db_models.users import User


class UserRepository(IUserRepository):
    def save(self, user: UserVO) -> None:
        new_user = User(
            id=user.id,
            name=user.name,
            email=user.email,
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        with SessionLocal() as db:
            db.add(new_user)
            db.commit()

    def find_by_email(self, email: str) -> UserVO:
        with SessionLocal() as db:
            query = select(
                User.id,
                User.name,
                User.email,
                User.password,
                User.created_at,
                User.updated_at,
            ).where(User.email == email)

            user = db.execute(query).one_or_none()

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
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )
                if user
                else None
            )

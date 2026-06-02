from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqldb://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@db/{settings.MYSQL_DATABASE}"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# 데이터베이스 세션과 관련 있음. 이 클래스의 객체가 생성되면 데이터베이스 세션이 생성됨.
SessionLocal = sessionmaker(
    autocommit=False,  # 별도 커밋 명령이 없으면 커밋이 자동으로 실행되지 않도록 False 처리. 만약 True로 설정하면 데이터베이스를 잘못 다뤘을 때 롤백 할 수 없다.
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

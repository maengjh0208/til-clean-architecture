from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 데이터베이스 설정
    MYSQL_ROOT_PASSWORD: str
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str


settings = Settings()

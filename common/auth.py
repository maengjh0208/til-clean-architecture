from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from config import settings

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/users/login")


class Role(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


@dataclass
class CurrentUser:
    id: str
    role: Role


# JWT 는 암호화(내용 숨김)가 아니라, 서명(위변조 방지) 이다.
# JWT 구조는 3 부분으로 나뉜다.
# header.payload.signature

# header 는 알고리즘 정보(HS256)
# payload 는 실제 데이터(user_id, exp 등), Base64로 인코딩된 것 뿐이어서 누구나 디코딩 가능
# signature 은 header + payload 를 SECRET_KEY 로 서명한 값
# 서버는 토큰을 받으면 signature 를 검증해서 이 토큰이 내가 발급한게 맞는지를 확인하는 것.
# 즉, payload 내용을 숨기는 것이 아니라 변조 여부를 검증한다.


def create_access_token(payload: dict, role: Role, expires_date: timedelta = timedelta(hours=6)) -> str:
    expire = datetime.now(timezone.utc) + expires_date
    # 토큰 만료 시간을 페이로드에 추가한다.
    payload.update(
        {
            "role": role,
            "exp": expire,
        }
    )
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        # 검증 실패하면 JWTError, 성공하면 payload 를 반환
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def get_current_user(token: Annotated[str, Depends(oauth2_schema)]) -> CurrentUser:
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    role = payload.get("role")

    if not user_id or not role or role != Role.USER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return CurrentUser(
        id=user_id,
        role=Role(role),
    )


def get_admin_user(token: Annotated[str, Depends(oauth2_schema)]):
    payload = decode_access_token(token)

    role = payload.get("role")

    if not role or role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return CurrentUser(
        id="ADMIN_USER_ID",  # TODO: 어드민 유저를 어떻게 관리할지 아직 미정
        role=Role(role),
    )

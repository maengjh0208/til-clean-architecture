from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt

SECRET_KEY = "THIS_IS_SUPER_SECRET_KEY"
ALGORITHM = "HS256"


# JWT 는 암호화(내용 숨김)가 아니라, 서명(위변조 방지) 이다.
# JWT 구조는 3 부분으로 나뉜다.
# header.payload.signature

# header는 알고리즘 정보(HS256)
# payload는 실제 데이터(user_id, exp 등), Base64로 인코딩된 것 뿐이어서 누구나 디코딩 가능
# signature은 header + payload 를 SECRET_KEY 로 서명한 값
# 서버는 토큰을 받으면 signature를 검증해서 이 토큰이 내가 발급한게 맞는지를 확인하는 것.
# 즉, payload 내용을 숨기는 것이 아니라 변조 여부를 검증한다.


def create_access_token(payload: dict, expires_date: timedelta = timedelta(hours=6)) -> str:
    expire = datetime.now(timezone.utc) + expires_date
    # 토큰 만료 시간을 페이로드에 추가한다.
    payload.update({"exp": expire})
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

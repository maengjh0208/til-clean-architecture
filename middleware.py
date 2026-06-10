from fastapi import FastAPI, Request

from common.auth import CurrentUser, decode_access_token
from common.logger import logger
from context_vars import user_context


def create_middleware(app: FastAPI):
    @app.middleware("http")
    def get_current_user_middleware(request: Request, call_next):
        # 요청에 포함된 Authorization에 있는 JWT를 분석해 유저 정보를 추출하고
        # 유저 정보는 컨텍스트 변수로 저장한다.
        authorization = request.headers.get("Authorization")
        if authorization:
            splits = authorization.split(" ")
            if splits[0] == "Bearer":
                token = splits[1]
                payload = decode_access_token(token)
                user_id = payload.get("user_id")
                role = payload.get("role")

                user_context.set(
                    CurrentUser(
                        id=user_id,
                        role=role,
                    )
                )

        # 요청 URL 을 출력
        logger.info(request.url)

        response = call_next(request)
        return response

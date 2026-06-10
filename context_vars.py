from contextvars import ContextVar

from common.auth import CurrentUser

# 유저 정보를 저장할 컨텍스트. 토큰 없이 수행되는 API의 경우 None이 된다.
# 첫번쨰 인수("current_user")는 디버깅할 떄 식별용으로 쓴다.
# 실제 변수 접근은 파이썬 변수명(user_context)으로 한다.
user_context: CurrentUser | None = ContextVar("current_user", default=None)

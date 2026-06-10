import asyncio
from contextvars import ContextVar

from fastapi import APIRouter

# ContextVar 의 첫번쨰 인수는 컨텍스트 변수의 이름이다. 컨텍스트 변수는 여러 개 생성해서 관리할 수 있다.
# 컨텍스트 변수를 설정(set)하지 않은 상태에서 변수의 값을 읽으려고(get)하면 LookupError가 발생한다.
# 따라서 기본값은 설정해두는 것이 좋다.
foo_context: ContextVar[str] = ContextVar("foo", default="bar")

router = APIRouter(prefix="/context")


@router.get("")
async def context_test(var: str):
    foo_context.set(var)
    await asyncio.sleep(1)

    return {
        "var": var,
        "context_var": foo_context.get(),
    }

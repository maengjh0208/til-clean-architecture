# 백그라운드 작업 테스트

import asyncio

from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix="/bg-task-test")


async def perform_task(task_id: int):
    await asyncio.sleep(3)
    print(f"{task_id}번 태스크 수행 완료")


# POST /bg-task-test - 백그라운드 작업 테스트
@router.post("")
def create_task(task_id: int, background_tasks: BackgroundTasks):
    # BackgroundTasks.add_task()는 함수를 "등록"만 한다.
    # 실제 실행은 FastAPI 가 응답 반환 후에 알아서 처리한다.
    # 즉, 이 함수 나중에 실행해줘. 하고 넘기는 것 뿐.

    # FastAPI의 BackgroundTasks는 응답을 보낸 직후, 같은 이벤트 루푸에서 실행된다.
    # 즉 같은 프로세스, 같은 스레드에서 동작한다.
    # 응답을 빨리 주되, 가벼운 후처리(이메일 발송, 로그 기록 등)를 뒤에 하고 싶을 때 쓴다.
    # 진짜로 별도 프로세스/스레드가 필요한 경우 Celery 같은 별도 작업 큐를 쓰면 된다.
    background_tasks.add_task(perform_task, task_id)
    return {"message": "태스크가 생성되었습니다."}

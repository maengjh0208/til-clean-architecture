# 미들웨어 테스트


from datetime import time

from fastapi import FastAPI, Request


# main.py 에서 생성한 FastAPI 객체(app)을 전달받는다.
def create_sample_middleware(app: FastAPI):

    # @app.middleware decorator를 미들웨어 함수에 선언해 이 함수가 미들웨어임을 알린다.
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()

        # 미들웨어가 여러개 등록되어 있으면 다음 미들웨어로 요청 객체를 전달한다. 또는 엔드포인트 함수로 요청을 전달한다.
        response = await call_next(request)

        process_time = time.time() - start_time
        # 응답 객체의 헤더에 수행 시간을 기록한다.
        response.headers["X-Process-Time"] = str(process_time)

        return response

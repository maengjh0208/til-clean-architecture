from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from containers import Container
from example.ch10_01.background_task import router as bg_router
from example.ch11_01.middleware import create_sample_middleware
from note.interface.controllers.note_controller import router as note_rotuer
from user.interface.controllers.user_controller import router as user_router

app = FastAPI()

# FastAPI 객체에 동적으로 속성 추가
# 앱 인스턴스에 컨테이너를 붙여두면 어디서든 request.app.container 로 접근이 가능하다.
app.container = Container()

app.include_router(user_router)
app.include_router(note_rotuer)
app.include_router(bg_router)

# create_sample_middleware 함수를 따로 선언한 이유는 @app.middleware 데코레이터를 사용하기 위함인데,
# app 객체가 선언되어 있는 main.py 가 아닌 모듈에서 이 데코레이터가 동작하지 않기 때문이다.
# 만약 이 방식이 마음에 들지 않으면, add_process_time_header 함수만 데코레이터 없이 선언하고
# main.py 에서 다음과 같이 미들웨어를 직접 연결할 수도 있다.
# app.middleware("http")(add_process_time_header)
create_sample_middleware(app)


# BaseModel 타입 검증 실패시 기본적으로 422 에러가 발생한다. 이거를 400 상태코드로 변경
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=400,
        content=exc.errors(),
    )


@app.get("/healthcheck")
def hello():
    return {"status": "ok"}

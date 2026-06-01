from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from user.interface.controllers.user_controller import router as user_router

app = FastAPI()

app.include_router(user_router)


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

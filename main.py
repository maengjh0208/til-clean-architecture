from fastapi import FastAPI

app = FastAPI()


@app.get("/healthcheck")
def hello():
    return {"status": "ok"}

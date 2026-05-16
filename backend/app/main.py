from app.api.v1.api import api_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "CrackedInfo API Running :)"}

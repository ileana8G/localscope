from fastapi import FastAPI

from backend.app.api.localities import router as localities_router

app = FastAPI(title="LocalScope API")

app.include_router(localities_router)


@app.get("/")
def root():
    return {"message": "LocalScope API is running"}
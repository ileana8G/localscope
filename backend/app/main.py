from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.localities import router as localities_router

app = FastAPI(title="LocalScope API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(localities_router)

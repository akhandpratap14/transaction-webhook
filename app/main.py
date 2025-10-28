import logging
from fastapi import FastAPI, Request
from app.config import settings
from app.routers import routers
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application is starting...")

    yield 

    logger.info("Application is shutting down...")


app = FastAPI(lifespan=lifespan)

allowed_origins = settings.ALLOWED_ORIGINS.split(",")

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Transaction Webhook API is running 🚀"}

@app.get("/ping")
async def read_root(request: Request):
    origin = request.headers.get("origin")
    return {
        "message": "pong",
        "origin": request.headers.get("origin"),
        "host": request.headers.get("host"),
        "referer": request.headers.get("referer"),
        "user-agent": request.headers.get("user-agent"),
        "x-forwarded-for": request.headers.get("x-forwarded-for"),
        "all_headers": dict(request.headers),
        "client": {"host": request.client.host, "port": request.client.port},
        "allowed_origins": allowed_origins,
    }


for router in routers:
    app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.base_class import Base
from src.db.session import engine
from src.api.v1.router import api_router
import src.models  # noqa: F401 — register all models with SQLAlchemy


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="InnerPlog",
    description="A blogging platform to encourage mindful writing and self-expression",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def health_check():
    return {"status": "ok", "app": "InnerPlog"}

from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.models.item import Item
from app.routers.item import item_router
from app.utils.log import init_logging, logger

init_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up")
    client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(client[settings.mongodb_name], document_models=[Item])
    yield
    logger.info("Application shutting down")


app = FastAPI(lifespan=lifespan)

app.include_router(item_router, prefix="/items", tags=["items"])

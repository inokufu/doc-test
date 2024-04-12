from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.models.item import Item
from app.routers.item import item_router
from app.utils.log import init_logging

init_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Check if MongoDB URL and MongoDB Database Name are provided
    if settings.mongodb_url is None or settings.mongodb_name is None:
        raise ValueError(
            "MongoDB URL and MongoDB Database Name must be provided in the environment variables"
        )

    # Connect to MongoDB and initialize Beanie ODM
    client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(client[settings.mongodb_name], document_models=[Item])
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(item_router, prefix="/items", tags=["items"])

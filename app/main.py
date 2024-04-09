from typing import Optional
from fastapi import FastAPI
from app.models import Item, Items
from app.database import item, items
from app.log import logger

app = FastAPI()

@app.post(
    "/items/",
    response_model=Item, 
    summary="Create an item",
    description="Create an item with all the information",
    response_description="The created item",
    tags=["items"]
)
async def create_item(item: Item):
    logger.info(f"Creating item: {item}")
    return item

@app.get(
    "/items/",
    response_model=Items,
    summary="Read items",
    description="Read all items",
    response_description="A list of all items",
    tags=["items"]
)
async def read_items():
    logger.info(f"Reading items: {items}")
    return items

@app.get(
    "/items/{item_id}",
    response_model=Optional[Item],
    summary="Read an item",
    description="Read an item by its ID",
    response_description="The item with the ID",
    tags=["items"]
)
async def read_item_by_id(item_id: int):
    try:
        return items[item_id]
    except IndexError:
        logger.error(f"Item with ID {item_id} not found")
        return None

from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.models.item import Item, UpdateItem

item_router = APIRouter()


async def get_item(item_id: PydanticObjectId) -> Item:
    item = await Item.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@item_router.post("/", response_model=Item, response_model_by_alias=False)
async def create_item(item: Item):
    return await item.create()


@item_router.get("/", response_model=List[Item], response_model_by_alias=False)
async def get_items():
    return await Item.find_all().to_list()


@item_router.get("/{item_id}", response_model=Item, response_model_by_alias=False)
async def get_item_by_id(item: Item = Depends(get_item)):
    return item


@item_router.put("/{item_id}", response_model=Item, response_model_by_alias=False)
async def update_item(item_id: PydanticObjectId, item: UpdateItem):
    current_item = await get_item(item_id)
    return await current_item.set(item.model_dump(exclude_unset=True))


@item_router.delete("/{item_id}")
async def delete_item(item: Item = Depends(get_item)):
    await item.delete()
    return {"status": "deleted"}

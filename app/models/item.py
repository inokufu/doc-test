from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class ItemId(BaseModel):
    item_id: PydanticObjectId = Field(..., title="The item ID")


class CreateItem(BaseModel):
    name: str = Field(..., title="The name of the item", min_length=1, max_length=100)
    description: str = Field(..., title="The description of the item", max_length=300)
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: float = Field(..., title="Tax rate")


class UpdateItem(BaseModel):
    name: Optional[str] = Field(
        None, title="The name of the item", min_length=1, max_length=100
    )
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: Optional[float] = Field(
        None, gt=0, description="The price must be greater than zero"
    )
    tax: Optional[float] = Field(None, title="Tax rate")


class Item(Document, CreateItem):
    ...

    class Settings:
        name = "items_collection"

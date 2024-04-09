from typing import List
from pydantic import BaseModel, Field, RootModel

class Item(BaseModel):
    name: str = Field(..., title="The name of the item", min_length=1, max_length=100)
    description: str = Field(None, title="The description of the item", max_length=300)
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: float = Field(None, title="Tax rate")

class Items(RootModel):
    root: List[Item]

from app.models import Item, Items

item: Item = Item(name="Item Name", description="An item", price=42.0, tax=3.2)
items: Items = Items(root=[item])

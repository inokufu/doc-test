from typing import Callable

import pytest
import pytest_asyncio
from beanie import PydanticObjectId, init_beanie
from fastapi import FastAPI
from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.models.item import Item
from app.routers.item import item_router


@pytest_asyncio.fixture(autouse=True, scope="session")
async def test_app():
    """Create a test FastAPI application with an in-memory MongoDB client.

    Yields:
        FastAPI: A FastAPI application instance.
    """
    # Create a new instance of FastAPI.
    app = FastAPI()
    app.include_router(item_router, prefix="/items", tags=["items"])

    # Set up the in-memory MongoDB and initialize Beanie with mocked client.
    client = AsyncMongoMockClient()
    await init_beanie(database=client.db_name, document_models=[Item])

    # We "yield" the application for HTTPX to use.
    yield app


@pytest_asyncio.fixture(autouse=True, scope="function")
async def empty_db():
    """Clear the database before and after each test.

    Args:
        request (pytest.FixtureRequest): The request object for the test; allows to access the test function name.
    """
    # Clear the database before each test
    await Item.delete_all()
    yield
    # Clear the database after each test
    await Item.delete_all()


@pytest_asyncio.fixture(scope="function")
async def populate_db() -> Callable:
    """Insert test items into the database."""

    async def _populate_db(nb_items: int = 3):
        """Insert test items into the database.

        Args:
            nb_items (int, optional): Number of items to insert into the database. Defaults to 3.
        """
        items = [
            Item(
                name=f"Item {i}",
                description=f"Description {i}",
                price=(i * 10.0),
                tax=(i * 1.0),
            )
            for i in range(1, nb_items + 1)
        ]
        await Item.insert_many(items)

    return _populate_db


@pytest.mark.asyncio
async def test_create_item(test_app: FastAPI):
    """Test create_item returns the created item.

    Args:
        test_app (FastAPI): A FastAPI application instance.
    """
    item_to_create = Item(
        name="Test Item",
        description="A test item",
        price=100.0,
        tax=10.0,
    )
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.post(
            "/items/", json=item_to_create.model_dump(exclude_defaults=True)
        )
    assert response.status_code == 200, "Expected a 200 response code"
    assert Item(**response.json()), "Expected an Item instance"

    created_item = Item(**response.json())
    assert created_item.id is not None, "Expected an item with an ID"
    assert isinstance(
        created_item.id, PydanticObjectId
    ), "Expected the ID to be a valid PydanticObjectId"


@pytest.mark.asyncio
async def test_get_items(test_app: FastAPI, populate_db: Callable):
    """Test get_items returns a list of items.

    Args:
        test_app (FastAPI): A FastAPI application instance.
        populated_db (None): A fixture to populate the database with test items.
    """
    # Populate the database with N test items
    n_items_to_insert: int = 3
    await populate_db(n_items_to_insert)

    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.get("/items/")

        assert response.status_code == 200, "Expected a 200 response code"
        assert isinstance(response.json(), list), "Expected a list of items"
        assert all(
            Item(**item) for item in response.json()
        ), "Expected a list of Item instances"
        assert (
            len(response.json()) == n_items_to_insert
        ), "Expected the number of items to match the number of inserted items"

        items = [Item(**item) for item in response.json()]
        assert all(
            item.id is not None and isinstance(item.id, PydanticObjectId)
            for item in items
        ), "Expected all items to have an ID"

    # Empty the db
    await Item.delete_all()

    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.get("/items/")
        assert (
            response.status_code == 200
        ), "Expected a 200 response code even when no items are present in the database"
        assert response.json() == [], "Expected an empty list when no items are present"


@pytest.mark.asyncio
async def test_get_item_by_id(test_app: FastAPI, populate_db: Callable):
    # Populate the database with N test items
    await populate_db(3)

    # Get the populated items
    items = await Item.find_all().to_list()

    # Test getting each item by ID
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        for item in items:
            response = await ac.get(f"/items/{item.id}")

            assert response.status_code == 200, "Expected a 200 response code"
            assert Item(**response.json()), "Expected an Item instance"
            assert (
                Item(**response.json()).id == item.id
            ), "Expected the ID to match the requested item ID"

    # Delete one item
    item_to_delete = items[0]
    await item_to_delete.delete()

    # Test getting the deleted item by ID
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.get(f"/items/{item_to_delete.id}")
        assert (
            response.status_code == 404
        ), "Expected a 404 response code for a unknown but valid item ID"

        response = await ac.get("/items/UNKNOWN")
        assert (
            response.status_code == 422
        ), "Expected a 422 response code for an invalid item ID"


@pytest.mark.asyncio
async def test_update_item(test_app: FastAPI, populate_db: Callable):
    # Populate the database with N test items
    await populate_db(1)

    # Get the populated items
    items = await Item.find_all().to_list()

    # Full update test
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        for item in items:
            updated_item = Item(
                name=f"Updated {item.name}",
                description=f"Updated {item.description}",
                price=(item.price + 10.0),
                tax=(item.tax + 1.0),
            )
            response = await ac.put(
                f"/items/{item.id}", json=updated_item.model_dump(exclude_defaults=True)
            )

            assert response.status_code == 200, "Expected a 200 response code"
            assert Item(**response.json()), "Expected an Item instance"
            assert (
                Item(**response.json()).id == item.id
            ), "Expected the ID to match the requested item ID"
            assert (
                Item(**response.json()).name == updated_item.name
            ), "Expected the name to be updated"
            assert (
                Item(**response.json()).description == updated_item.description
            ), "Expected the description to be updated"
            assert (
                Item(**response.json()).price == updated_item.price
            ), "Expected the price to be updated"
            assert (
                Item(**response.json()).tax == updated_item.tax
            ), "Expected the tax to be updated"

    # Partial update test
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        for item in items:
            jsonified_item = item.model_dump(exclude_defaults=True)

            for field_name, field_value in jsonified_item.items():
                if isinstance(field_value, str):
                    field_value = f"Updated {field_value}"
                elif isinstance(field_value, float):
                    field_value = field_value + 10.0
                elif isinstance(field_value, bool):
                    field_value = not field_value
                elif isinstance(field_value, int):
                    field_value = field_value + 1
                else:
                    continue

                # TODO: Handle other types ? --> We may need to do it field by field, would be much easier

                response = await ac.put(
                    f"/items/{item.id}", json={field_name: field_value}
                )

                assert response.status_code == 200, "Expected a 200 response code"
                assert Item(**response.json()), "Expected an Item instance"
                assert (
                    Item(**response.json()).id == item.id
                ), "Expected the ID to match the requested item ID"

                if field_name != "id":
                    assert (
                        response.json()[field_name] == field_value
                    ), "Expected the field value to be updated"
                else:
                    assert response.json()[field_name] == str(
                        item.id
                    ), "Expected the field value to be updated"

    # Delete one item, and try to update it
    item_to_delete = items[0]
    await item_to_delete.delete()

    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.put(f"/items/{item_to_delete.id}", json={})
        assert (
            response.status_code == 404
        ), "Expected a 404 response code for an unknown but valid item ID"

        response = await ac.put("/items/UNKNOWN", json={})
        assert (
            response.status_code == 422
        ), "Expected a 422 response code for an invalid item ID"


@pytest.mark.asyncio
async def test_delete_item(test_app: FastAPI, populate_db: Callable):
    # Populate the database with N test items
    await populate_db(1)

    # Get the populated items
    items = await Item.find_all().to_list()

    # Delete test
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        for item in items:
            response = await ac.delete(f"/items/{item.id}")

            assert response.status_code == 200, "Expected a 200 response code"

            response = await ac.get(f"/items/{item.id}")
            assert (
                response.status_code == 404
            ), "Expected a 404 response code for a deleted item ID"

    # Delete one item, and try to delete it again
    item_to_delete = items[0]
    await item_to_delete.delete()

    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.delete(f"/items/{item_to_delete.id}")
        assert (
            response.status_code == 404
        ), "Expected a 404 response code for an unknown but valid item ID"

        response = await ac.delete("/items/UNKNOWN")
        assert (
            response.status_code == 422
        ), "Expected a 422 response code for an invalid item ID"

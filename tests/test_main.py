from fastapi.testclient import TestClient

from app.main import app
from app.models import Item

client = TestClient(app)


def test_create_item():
    response = client.post(
        "/items/",
        json={
            "name": "Item Name",
            "description": "An item",
            "price": 42.0,
            "tax": 3.2,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "name": "Item Name",
        "description": "An item",
        "price": 42.0,
        "tax": 3.2,
    }
    assert Item(**response.json())


def test_read_items():
    response = client.get("/items/")
    assert response.status_code == 200
    # Check that the response is a list
    assert isinstance(response.json(), list)
    # Check that the response is a list of dictionaries
    assert all(Item(**item) for item in response.json())


def test_read_item_by_id():
    response = client.get("/items/0")
    assert response.status_code == 200
    assert Item(**response.json())

    response = client.get("/items/UNKNOWN")
    assert response.status_code == 422

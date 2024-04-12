import os

from app.config import Settings


def test_settings():
    s = Settings()
    assert s.mongodb_url == os.environ.get("MONGODB_URL")
    assert s.mongodb_name == os.environ.get("MONGODB_NAME")


# TODO: Find a way to override the .env file for testing purposes

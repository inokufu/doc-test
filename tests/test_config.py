import os
from datetime import datetime
from unittest.mock import patch

import pytest

from app.config import Settings

MONGODB_URL = "mongodb://localhost:27017"
MONGODB_NAME = "testdb"


@pytest.fixture(autouse=True, scope="session")
def remove_env_file():
    """Move (by renaming) the .env file to a temporary file, before running each test."""
    original_env_file = ".env"
    temp_save_env_file = f".env.temp.test.{datetime.timestamp(datetime.now())}"

    # Check if the .env file exists
    if os.path.exists(original_env_file):
        # If yes, rename the file to a temp file
        os.rename(original_env_file, temp_save_env_file)
        yield
        # Rename the file back to the original name
        os.rename(temp_save_env_file, original_env_file)
    # If the file does not exist, do nothing
    else:
        yield


@pytest.fixture(scope="function")
def create_dummy_env_file():
    """Create a dummy .env file with Settings variables for testing."""
    env_file_path = ".env"
    content = [f"MONGODB_URL={MONGODB_URL}", f"MONGODB_NAME={MONGODB_NAME}"]
    # Write the content to the dummy file
    with open(env_file_path, "w") as file:
        for line in content:
            file.write(f"{line}\n")
    yield
    # Check if the file exists (it should exist because created in the first part of the fixture)
    if os.path.exists(env_file_path):
        # Delete the file
        os.remove(env_file_path)


def test_missing_required_settings():
    """Test behavior when some required settings are missing."""
    with patch.dict("os.environ", {}, clear=True):
        settings = Settings()
        assert settings.mongodb_url is None
        assert settings.mongodb_name is None

    with patch.dict("os.environ", {"MONGODB_URL": MONGODB_URL}, clear=True):
        settings = Settings()
        assert settings.mongodb_url == MONGODB_URL
        assert settings.mongodb_name is None

    MONGODB_NAME = "testdb"
    with patch.dict("os.environ", {"MONGODB_NAME": MONGODB_NAME}, clear=True):
        settings = Settings()
        assert settings.mongodb_url is None
        assert settings.mongodb_name == MONGODB_NAME


def test_loads_settings_from_environment():
    """Test that settings are loaded correctly from environment variables."""
    var_mongodb_url = f"var_{MONGODB_URL}"
    var_mongodb_name = f"var_{MONGODB_NAME}"
    with patch.dict(
        "os.environ",
        {"MONGODB_URL": var_mongodb_url, "MONGODB_NAME": var_mongodb_name},
        clear=True,
    ):
        settings = Settings()
        assert settings.mongodb_url == var_mongodb_url
        assert settings.mongodb_name == var_mongodb_name


def test_loads_settings_from_env_file(create_dummy_env_file):
    """Test that settings are loaded correctly from the env file by the settings class."""
    with patch.dict("os.environ", {}, clear=True):
        settings = Settings()
        assert settings.mongodb_url == MONGODB_URL
        assert settings.mongodb_name == MONGODB_NAME


def test_loads_settings_from_env_file_overrides_default(create_dummy_env_file):
    """Test that env file values are overrided by the environment variables."""
    var_mongodb_url = f"var_{MONGODB_URL}"
    var_mongodb_name = f"var_{MONGODB_NAME}"
    with patch.dict("os.environ", {}, clear=True):
        with patch.dict("os.environ", {"MONGODB_URL": var_mongodb_url}, clear=False):
            settings = Settings()
            assert settings.mongodb_url == var_mongodb_url
            assert settings.mongodb_name == MONGODB_NAME

        with patch.dict("os.environ", {"MONGODB_NAME": var_mongodb_name}, clear=False):
            settings = Settings()
            assert settings.mongodb_url == MONGODB_URL
            assert settings.mongodb_name == var_mongodb_name

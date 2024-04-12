from unittest.mock import patch

import pytest
from fastapi import FastAPI

from app.main import lifespan


@pytest.mark.asyncio
async def test_lifespan_with_no_db_settings():
    """Test the lifespan function to ensure it handles missing DB settings correctly."""
    with patch("app.config.settings.mongodb_url", new=None), patch(
        "app.config.settings.mongodb_name", new=None
    ):
        app_instance = FastAPI()
        with pytest.raises(ValueError):
            async with lifespan(app_instance):
                pass

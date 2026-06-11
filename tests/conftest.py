import pytest
import os
from app.core.config import settings

@pytest.fixture(scope="session", autouse=True)
def test_env_setup():
    # Ensure we use a test database
    settings.DB_PATH = "test_app.db"
    yield
    # Final cleanup
    if os.path.exists("test_app.db"):
        try:
            os.remove("test_app.db")
        except:
            pass
    if os.path.exists("test_e2e.db"):
        try:
            os.remove("test_e2e.db")
        except:
            pass

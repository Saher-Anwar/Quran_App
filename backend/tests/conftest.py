"""Pytest configuration and fixtures for testing with real database."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.database import get_db, AsyncSessionLocal


@pytest.fixture
async def db_session() -> AsyncSession:
    """
    Provide a database session for tests.
    Uses the real database configured in settings.

    Each test gets a fresh session that rolls back changes after the test.
    """
    async with AsyncSessionLocal() as session:
        yield session
        # Rollback any changes made during the test
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession):
    """
    Provide an async test client with database dependency override.

    This ensures all API calls during tests use the test database session.
    """
    from httpx import ASGITransport

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def sample_verse_data():
    """Provide sample verse data for tests."""
    return {
        "surah_number": 1,
        "verse_number": 1,
        "text_arabic": "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
        "text_simple": "بسم الله الرحمن الرحيم",
        "translation_english": "In the name of Allah, the Entirely Merciful, the Especially Merciful."
    }

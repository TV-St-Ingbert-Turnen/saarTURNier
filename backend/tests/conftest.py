"""Backend testing configuration."""

import os
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.database import Base
from app.main import create_app


@pytest.fixture(scope="session")
async def test_db_engine():
    """Create test database engine."""
    test_db_url = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    engine = create_async_engine(test_db_url, echo=False, future=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    """Create test database session."""
    async_session = async_sessionmaker(test_db_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def app():
    """Create FastAPI application."""
    app = create_app()
    yield app


@pytest.fixture
async def client(app):
    """Create test client."""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def test_user():
    """Create test user data."""
    return {
        "id": "test-user-1",
        "login": "judge1",
        "role": "judge",
        "competition_id": "comp-1",
    }


@pytest.fixture
def test_competition():
    """Create test competition data."""
    return {
        "id": "comp-1",
        "name": "Test Competition",
        "organizer": "Test Organizer",
    }

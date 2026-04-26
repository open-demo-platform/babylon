"""Pytest fixtures for catalog-api tests."""
import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Mock environment variables before importing app
os.environ['BABYLON_ADMIN_ENABLED'] = 'false'
os.environ['BABYLON_RATINGS_ENABLED'] = 'false'
os.environ['SALESFORCE_ENABLED'] = 'false'
os.environ['DEFAULT_CATALOG_NAMESPACES'] = 'babylon-catalog'
os.environ['BABYLON_NAMESPACE'] = 'babylon-catalog'  # Required for app startup

from app import routes

@pytest.fixture
async def client(aiohttp_client):
    """Create test client for catalog-api."""
    # Create a fresh app instance for each test
    test_app = web.Application()
    test_app.add_routes(routes)
    return await aiohttp_client(test_app)

@pytest.fixture
def mock_admin_user():
    """Mock admin user headers."""
    return {
        'X-Forwarded-User': 'admin',
        'X-Forwarded-Email': 'admin@example.com'
    }

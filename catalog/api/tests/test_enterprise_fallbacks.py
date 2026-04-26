"""Test enterprise service fallback behavior."""
import pytest
import json

@pytest.mark.asyncio
async def test_admin_incidents_returns_empty_array(client, mock_admin_user):
    """Test /api/admin/incidents returns [] when admin service disabled."""
    resp = await client.get(
        '/api/admin/incidents?status=active&interface=rhpds',
        headers=mock_admin_user
    )

    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, list), "Should return array"
    assert data == [], "Should return empty array"

@pytest.mark.asyncio
async def test_bookmarks_get_returns_empty_object(client, mock_admin_user):
    """Test GET /api/user-manager/bookmarks returns {bookmarks: []} when ratings disabled."""
    resp = await client.get(
        '/api/user-manager/bookmarks',
        headers=mock_admin_user
    )

    assert resp.status == 200
    data = await resp.json()
    assert 'bookmarks' in data, "Should have bookmarks key"
    assert isinstance(data['bookmarks'], list), "bookmarks should be array"
    assert data['bookmarks'] == [], "Should return empty bookmarks array"

@pytest.mark.asyncio
async def test_bookmarks_post_returns_empty_object(client, mock_admin_user):
    """Test POST /api/user-manager/bookmarks returns {bookmarks: []} when ratings disabled."""
    resp = await client.post(
        '/api/user-manager/bookmarks',
        headers=mock_admin_user,
        json={'asset_uuid': 'test-123'}
    )

    assert resp.status == 201
    data = await resp.json()
    assert 'bookmarks' in data
    assert data['bookmarks'] == []

@pytest.mark.asyncio
async def test_bookmarks_delete_returns_empty_object(client, mock_admin_user):
    """Test DELETE /api/user-manager/bookmarks returns {bookmarks: []} when ratings disabled."""
    resp = await client.delete(
        '/api/user-manager/bookmarks?asset_uuid=test-123',
        headers=mock_admin_user
    )

    assert resp.status == 200
    data = await resp.json()
    assert 'bookmarks' in data
    assert data['bookmarks'] == []

@pytest.mark.asyncio
async def test_catalog_incident_active_incidents(client, mock_admin_user):
    """Test /api/catalog_incident/active-incidents returns {items: []} when reporting disabled."""
    resp = await client.get(
        '/api/catalog_incident/active-incidents?stage=prod',
        headers=mock_admin_user
    )

    assert resp.status == 200
    data = await resp.json()
    assert 'items' in data, "Response must have 'items' key for frontend"
    assert isinstance(data['items'], list), "items must be array"
    assert data['items'] == [], "Should return empty items array"
